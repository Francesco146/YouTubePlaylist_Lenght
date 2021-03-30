# coding: utf-8
# importing all the modules that i need
from oms import oreMinutiSecondi
from googleapiclient.discovery import build
from googleapiclient import discovery
from flask import Flask, send_from_directory
from flask_restful import Resource, Api, reqparse
from redis import Redis
from datetime import timedelta
import markdown
import time
import json
import re
import os


print("Getting the API Key from docker-compose.yml...")
# get the api key from the os environment, the docker-compose.yml in this case
youtube_api_key = os.getenv("YOUR_YOUTUBE_V3_API_KEY")
print("\033[92mAPI Key taken. ✓\033[0m")
print("Loading JSON YouTube API File...")
path_json = 'rest.json'
with open(path_json) as f:
    # loading this .json file is used because googleapiclient has some problem withe the api key, so this json is a sort of auto configuration taken from the internet
    service = json.load(f, )
print("\033[92mJSON YouTube API File Loaded. ✓\033[0m")
print("Creating Flask APP Server...")
flask_app = Flask(__name__)  # initialize Flask app
print("\033[92mFlask APP Server created. ✓\033[0m")
print("Connecting to Redis Database and creating the Cache System...")
# connect to Redis server, redis is the hostname of the redis container on the application’s network
cache = Redis(host='redis', port=6379)
print("\033[92mConnected to Redis Database, Cache System has started. ✓\033[0m")


# add a decorator to the flask app, in position /, only on method GET
@flask_app.route("/", methods=["GET"])
def index():  # defining what to do if get a GET on route /
    """Main Page of the Flask WebServer

    :param None: None

    :return: (html) Html from the README.md markdown file
    """
    with open('index.md', 'r') as index:
        # return a markdown -> html as index page
        return markdown.markdown(index.read())


# add a decorator to the flask app, in position /addUser, only on method GET
@flask_app.route("/addUser", methods=["GET"])
def addUser():  # defining what to do if get a GET on route /
    """Page for explaining how to add user

    :param None: None

    :return: (html) Html from the addUser.md markdown file
    """
    with open('addUser.md', 'r') as index:
        # return a markdown -> html as index page
        return markdown.markdown(index.read())


@flask_app.route('/favicon.ico')  # add a decorator in position /favicon.ico
def favicon():  # defining what to return in route /favicon.ico
    """Page Icon

    :param None: None

    :return: (file) favicon.ico
    """
    return send_from_directory(flask_app.root_path,
                               'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')  # return the file favicon.ico as image/vnd.microsoft.icon type


def write_json(idUser, passwdUser):
    """Write in users.json the new idUser and the passwdUser

    :param idUser: Username
    :param passwdUser: Password

    :return: (bool) True if user is added, False if user is already there
    """
    with open('users.json') as json_file:  # open the json file with the usernames and passwords
        data = json.load(json_file)  # from all the json file
        temp = data['users']  # get only the users array
        for i in range(len(temp)):  # check all the json user array
            if idUser in str(temp[i]):  # if the username is already there return False
                return False
        dataUser = {  # if the user is not there, construct the new user by using the given username and password
            "id": idUser,
            "passwd": passwdUser
        }
        temp.append(dataUser)  # add the new user to the initial user array
    # rewrite the users.json with the updated user array, then return True
    with open('users.json', 'w') as f:
        json.dump(data, f, indent=4, sort_keys=True)
    return True


class addUser(Resource):
    """addUser Class, contains the POST method, use for the addUser command

    :param Resource: Resource class, internal of flask restful

    :return: post()
    """

    def post(self):
        """Represents an abstract RESTful resource (POST METHOD)

        :param addUser: (addUser) self represents the instance of the class addUser

        :return: (json) json response, like error: {'message': 'error'}, {'message': 'user already there'}, success: {"message": "success, user added.", "user": `username - password`}
        """
        request_parser = reqparse.RequestParser(
        )  # initialize the object for analyzing the incoming request
        # get username and password field from the request
        request_parser.add_argument('username', required=True)
        request_parser.add_argument('password', required=True)
        request_args = request_parser.parse_args()
        username = request_args.get('username')
        passwd = request_args.get('password')
        try:
            # try to write the id and password in the json users.json
            usercheck = write_json(username, passwd)
        except Exception:
            return {'message': 'error'}, 500
        if usercheck == True:  # if the user is added
            output = username + " - " + passwd
            response = {
                "message": "success, user added.",
                "user": "" + output
            }
            return response, 200  # returning a success
        elif usercheck == False:  # if the user is already there return a error
            return {'message': 'user already there'}, 500


class QueryAPI(Resource):  # main class of the api, constructor of the api
    """Main Object of the API, contains the POST method, used for the response

    :param Resource: Resource class, internal of flask restful

    :return: post()
    """

    def post(self):  # defining what to do on POST, is the only method avaible for Object QueryAPI
        """Represents an abstract RESTful resource (POST METHOD)

        :param QueryAPI: (QueryAPI) self represents the instance of the class QueryAPI

        :return: (json) json response, like error: {'message': 'errore id non corretto'}, {'message': 'errore id non corretto o chiave api non corretta'} success: {'message': 'Success','tempoIMP': time_spent,'durata': playlist_duration,'counter': video_counter}
        """
        with open('users.json') as json_file:
            data = json.load(json_file)
            passwords = data['users']
        request_parser = reqparse.RequestParser(
        )  # initialize the object for analyzing the incoming request
        # get id field from the request
        request_parser.add_argument('id', required=True)
        request_parser.add_argument('user', required=True)
        request_parser.add_argument('key', required=True)
        # creating an array of arguments from the request
        request_args = request_parser.parse_args()
        user = request_args.get('user')
        key = request_args.get('key')
        for i in range(len(passwords)):
            if user in passwords[i]["id"] and key in passwords[i]["passwd"]:
                break
            else:
                return {'message': 'errore user o key non validi'}, 403
        # if the value of `id` is a Playlist ID, get it and pass
        if request_args.get('id').startswith("PL"):
            playlist_ID = request_args.get('id')
        else:  # otherwise
            try:
                playlist_ID = request_args.get('id').split('list=')[1].lstrip().split(
                    '&')[0]  # try getting the playlist ID from the possible link, structured as https://www.youtube.com/playlist?list=`playlist id`&index=1
            except Exception:  # is not a valid link, sending an error
                return {'message': 'errore id non corretto'}, 500

        youtube = discovery.build_from_document(
            service, developerKey=youtube_api_key)  # initializing the api from the loaded json and my api key (from google developer console)

        pattern_Hours = re.compile(r'(\d+)H')
        pattern_Minutes = re.compile(r'(\d+)M')
        # regex pattern to get the duration of the video, from the response of my second query
        pattern_Seconds = re.compile(r'(\d+)S')

        total_seconds = 0
        nextPageToken = None  # this is used because youtube in his response give at most 50 results at time, and you need to get the others results by using this token
        video_counter = 0
        start_time = time.time()  # start the timer

        while True:  # while theres video in the playlist
            playlist_request = youtube.playlistItems().list(part='contentDetails',
                                                            playlistId=playlist_ID,
                                                            pageToken=nextPageToken)  # preparing the first query, get the first 50 video from the playlist given playlist ID and page token
            try:
                playlist_response = playlist_request.execute()  # execute the previous query
            except Exception:  # if it returns an error, is because the google console developer is down, the playlist id is invalid, the api key is invalid or because your api has reached the max query per day
                # so return an error to sender
                return {'message': 'errore id non corretto o chiave api non corretta'}, 500

            video_IDS_Temp = []  # creating / clearing this array to store all of video IDs
            # creating / clearing this array to store all the video duration in seconds
            videos_duration = []

            # analyze the response returned from youtube
            for item in playlist_response['items']:
                # take the video ids and put them all in array video_IDS_Temp
                video_IDS_Temp.append(item['contentDetails']['videoId'])

            # creating / clearing this array to store all of video IDs that are not in redis cache system
            video_IDS_Final = []

            for j in range(len(video_IDS_Temp)):  # i check all the video ids one by one
                # if the video id is not in the redis database (so the get method return none)
                if cache.get(video_IDS_Temp[j]) == None:
                    # put the video id in the final array, in needs to be analyzed and get stored in the cache
                    video_IDS_Final.append(video_IDS_Temp[j])
                else:  # otherwise, the video is already in the redis database
                    # get the value from redis, so the duration in second of that video, increase the final total_seconds variable with the result
                    total_seconds += int(cache.get(video_IDS_Temp[j]))
                    video_counter += 1  # increase the video counter of the playlist by one

            video_request = youtube.videos().list(part="contentDetails",
                                                  id=','.join(video_IDS_Final))
            # get all the details (so also the duration) from the final array of video's ids that are not in the cache
            video_response = video_request.execute()

            for item in video_response['items']:  # analyze the response i get

                # take the duration of the video, the output will be something like this: 23M1S this means 23 minutes and 1 second
                duration = item['contentDetails']['duration']

                # get the hours, minutes and seconds from the video duration,using regex pattern created previously
                hours = pattern_Hours.search(duration)
                minutes = pattern_Minutes.search(duration)
                seconds = pattern_Seconds.search(duration)

                # take the int value from regex output, for example: for eliminate the H in 23H. i do the if statement because is possible that regex returns a None, if there is no match, so if hour is None i set them to 0
                hours = int(hours.group(1)) if hours else 0
                minutes = int(minutes.group(1)) if minutes else 0
                seconds = int(seconds.group(1)) if seconds else 0

                video_seconds = timedelta(hours=hours,
                                          minutes=minutes,
                                          seconds=seconds).total_seconds()  # take all the hours, minutes and seconds and calculate the total seconds

                # put the video duration - 1 (because YouTube in his thumbnails put 1 seconds more than the actual video duration) in the array of videos duration
                videos_duration.append(int(video_seconds) - 1)
                video_counter += 1  # increase the video counter
                # update the total seconds of the videos duration
                total_seconds += video_seconds - 1

            # take the next page token, used for getting the other video details
            nextPageToken = playlist_response.get('nextPageToken')

            for i in range(len(videos_duration)):  # check the array
                # set the video id and its duration in the cache, with an expiration time of 60 seconds
                cache.set(video_IDS_Final[i], videos_duration[i], ex=60)

            if not nextPageToken:  # no more videos, stop the loop
                break

        total_seconds = int(total_seconds)
        # get the hours, minutes and seconds from the total seconds
        minutes, seconds = divmod(total_seconds, 60)
        hours, minutes = divmod(minutes, 60)

        # stop the timer and get hours, minutes and seconds elapsed
        time_elapsed = int(round(time.time() - start_time, 0))
        minutes_elapsed, seconds_elapsed = divmod(time_elapsed, 60)
        hours_elapsed, minutes_elapsed = divmod(minutes_elapsed, 60)

        time_spent = oreMinutiSecondi(
            hours_elapsed, minutes_elapsed, seconds_elapsed, 0)  # get a grammatically correct string, given hours, minutes and seconds
        playlist_duration = oreMinutiSecondi(hours, minutes, seconds, 1)

        response = {
            'message': 'Success',
            'tempoIMP': time_spent,
            'durata': playlist_duration,
            'counter': video_counter
        }  # constructing the response

        video_IDS_Temp.clear()  # clear all the arrays
        video_IDS_Final.clear()
        videos_duration.clear()

        return response, 200  # send the response


def main():
    """Main function, used to start the API server, add the Main Class to API server and finally run the Flask App

    :param None: None

    :return: zero after shutting down the Flask App
    """
    print("Creating API from Flask APP...")
    flask_api = Api(flask_app)  # creating the api from flask app
    print("\033[92mAPI from Flask APP created. ✓\033[0m")
    print("Adding Main class to API...")
    # add the main class as a resource to the api, in route /
    flask_api.add_resource(QueryAPI, '/')
    flask_api.add_resource(addUser, '/addUser')
    print("\033[92mAdded Main class to API. ✓\033[0m")
    print("\033[92mRunning Flask APP Server in: localhost:9999. ✓\033[0m")
    # finally run the app on localhost:9999
    flask_app.run(host="0.0.0.0", port=9999)
    return 0  # when app is shutdown returns 0


if __name__ == '__main__':  # when file is being launched run the main function
    main()
