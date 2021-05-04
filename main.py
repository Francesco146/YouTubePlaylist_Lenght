#!/usr/bin/python
# -*- coding: utf-8 -*-

__title__ = 'Python API With Redis Back-end'
__author__ = "Francesco Marastoni"
__copyright__ = "Copyright 2021, Francesco Marastoni"
__credits__ = ["Francesco Marastoni"]
__license__ = "GPL"
__version__ = "1.7.0"
__revision__ = "1"
__maintainer__ = "Francesco Marastoni"
__email__ = "marastoni14@gmail.com"
__status__ = "Prototype"


# importing all the modules that i need

from googleapiclient.discovery import build
from googleapiclient import discovery
from flask import Flask, send_from_directory, redirect, url_for, render_template, request, session
from flask_restful import Resource, Api, reqparse
from redis import Redis
from datetime import timedelta
import markdown
import time
import json
import re
import os
import logging
import sys
sys.dont_write_bytecode = True # not create a __pycache__ folder
from oms import oreMinutiSecondi
from queryAPI import queryAPI


if __name__ == '__main__':  # when file is being launched run config part
    logging.basicConfig(level = logging.INFO, 
                        filename = "./logs/apilog.log", 
                        encoding = "utf-8", 
                        filemode = "a",
                        format = '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
                        datefmt = '%Y-%m-%d %H:%M:%S'
    ) # a logger that keep tracks of everything

    logging.info("Starting API Server...")
    logging.info("Getting the API Key from docker-compose.yml...")
    print("Getting the API Key from docker-compose.yml...")
    # get the api key from the os environment, the docker-compose.yml in this case
    youtube_api_key = os.getenv("YOUR_YOUTUBE_V3_API_KEY")
    logging.info("API Key taken. ✓")
    print("\033[92mAPI Key taken. ✓\033[0m")
    print("Loading JSON YouTube API File...")
    logging.info("Loading JSON YouTube API File...")
    with open('rest.json') as f:
        # loading this .json file is used because googleapiclient has some problem withe the api key, so this json is a sort of auto configuration taken from the internet
        service = json.load(f, )
    print("\033[92mJSON YouTube API File Loaded. ✓\033[0m")
    logging.info("JSON YouTube API File Loaded. ✓")
    print("Creating Flask APP Server...")
    logging.info("Creating Flask APP Server...")
    flask_app = Flask(__name__)  # initialize Flask app
    print("\033[92mFlask APP Server created. ✓\033[0m")
    logging.info("Flask APP Server created. ✓")
    print("Connecting to Redis Database and creating the Cache System...")
    logging.info("Connecting to Redis Database and creating the Cache System...")
    # connect to Redis server, redis is the hostname of the redis container on the application’s network
    cache = Redis(host = 'redis', port = 6379)
    print("\033[92mConnected to Redis Database, Cache System has started. ✓\033[0m")
    logging.info("Connected to Redis Database, Cache System has started. ✓")


# add a decorator to the flask app, in position /, only on method GET
@flask_app.route("/", methods = ["GET"])
def home():
    """Home Page of the Web App

    :param None: None

    :return: (html) At the route / return the Html `index.html`
    """
    return render_template("index.html")  # return index.html

# add a decorator to the flask app, in position /api-documentation, only on method GET


@flask_app.route("/loading", methods = ["GET", "POST"])
def loading():
    """Loading page, not a physical html page, just a buffering point

    :param None: None

    :return: (String) PlayList ID from the form on index.html OR (html) error.html
    """
    try:  # split the string taken from `input` in the form in index.html, try getting the playlist ID
        URL = request.form["input"].split('list=')[1].lstrip().split('&')[0]
    except:
        # if it fails call the error route of the WebApp
        logging.warning("Bad PL-URL WebApp")
        return redirect(url_for("error"))
    # otherwise give the playlist id to the query route
    return redirect(url_for("query", playlistURL = URL))

# add a decorator to the flask app, in position /api-documentation, only on method GET


@flask_app.route("/error", methods = ["GET"])
def error():
    """Error page of the WebApp

    :param None: None

    :return: (html) render the error.html page
    """
    return render_template(template_name_or_list = "error.html")

# add a decorator to the flask app, in position /api-documentation, only on method GET


@flask_app.route("/query/<playlistURL>", methods = ["GET", "POST"])
def query(playlistURL):
    """Query the youtube api and display the results

    :param playlistURL: PlayList ID

    :type playlistURL: String

    :return: (html) query.html rendered with the result the queryAPI gave me
    """
    responseWebApp = queryAPI(service, youtube_api_key, cache,
                              playlistURL)  # call the function that analyze the data and store them in the cache system
    # return the page
    return render_template(template_name_or_list = "query.html", 
                           tempoIMP_output = responseWebApp["tempoIMP"], 
                           durata_output = responseWebApp["durata"], 
                           counter_output = str(responseWebApp["counter"])
    )


# add a decorator to the flask app, in position /api-documentation, only on method GET
@flask_app.route("/api-documentation", methods = ["GET"])
def index():  # defining what to do if get a GET on route /api-documentation
    """API Documentation Page of the Flask WebServer

    :param None: None

    :return: (html) Html from the README.md markdown file
    """
    with open('apiDocs.md', 'r') as index:
        # return a markdown -> html as index page
        return markdown.markdown(text = index.read())


# add a decorator to the flask app, in position /addUser, only on method GET
@flask_app.route("/addUser", methods = ["GET"])
def addUser():  # defining what to do if get a GET on route /addUser
    """Page for explaining how to add user

    :param None: None

    :return: (html) Html from the addUser.md markdown file
    """
    with open('addUser.md', 'r') as index:
        # return a markdown -> html as index page
        return markdown.markdown(text = index.read())


@flask_app.route('/favicon.ico')  # add a decorator in position /favicon.ico
def favicon():  # defining what to return in route /favicon.ico
    """Page Icon

    :param None: None

    :return: (file) favicon.ico
    """
    return send_from_directory(directory = flask_app.root_path + "static/",
                               filename = 'favicon.ico',
                               mimetype = 'image/vnd.microsoft.icon')  # return the file favicon.ico as image/vnd.microsoft.icon type


def write_json(idUser, passwdUser):
    """Write in users.json the new idUser and the passwdUser

    :param idUser: Username
    :param passwdUser: Password

    :type idUser: String
    :type passwdUser: String

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
        json.dump(data, f, indent = 4, sort_keys = True)
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
        request_parser.add_argument('username', required = True)
        request_parser.add_argument('password', required = True)
        request_args = request_parser.parse_args()
        username = request_args.get('username')
        passwd = request_args.get('password')
        try:
            # try to write the id and password in the json users.json
            usercheck = write_json(idUser = username, passwdUser = passwd)
        except Exception:
            logging.warning("Not Able to Write in the Json File")
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
        request_parser.add_argument('id', required = True)
        request_parser.add_argument('user', required = True)
        request_parser.add_argument('key', required = True)
        # creating an array of arguments from the request
        request_args = request_parser.parse_args()
        user = request_args.get('user')
        key = request_args.get('key')
        for i in range(len(passwords)):
            if user in passwords[i]["id"] and key in passwords[i]["passwd"]:
                break
            else:
                logging.warning("Not Authenticated User")
                return {'message': 'errore user o key non validi'}, 403
        # if the value of `id` is a Playlist ID, get it and pass
        if request_args.get('id').startswith("PL"):
            playlist_ID = request_args.get('id')
        else:  # otherwise
            try:
                playlist_ID = request_args.get('id').split('list=')[1].lstrip().split(
                    '&')[0]  # try getting the playlist ID from the possible link, structured as https://www.youtube.com/playlist?list=`playlist id`&index=1
            except Exception:  # is not a valid link, sending an error
                logging.warning("Bad PL-ID API")
                return {'message': 'errore id non corretto'}, 500
        # call the actual function that analyze the data, store them in the cache and returns the response
        response = queryAPI(service = service, 
                            youtube_api_key = youtube_api_key,
                            cache = cache,
                            playlist_ID = playlist_ID
        )
        return response, 200  # send the response


def main():
    """Main function, used to start the API server, add the Main Class to API server and finally run the Flask App

    :param None: None

    :return: zero after shutting down the Flask App
    """
    print("Creating API from Flask APP...")
    logging.info("Creating API from Flask APP...")
    flask_api = Api(flask_app)  # creating the api from flask app
    print("\033[92mAPI from Flask APP created. ✓\033[0m")
    logging.info("API from Flask APP created. ✓")
    print("Adding Main class and User Class to API...")
    logging.info("Adding Main class and User Class to API...")
    # add the main class as a resource to the api, in route /api-entrypoint
    flask_api.add_resource(QueryAPI, '/api-entrypoint')
    flask_api.add_resource(addUser, '/api-entrypoint/addUser')
    print("\033[92mAdded Main class to API (/api-entrypoint) (/api-entrypoint/addUser). ✓\033[0m")
    logging.info("Added Main class to API (/api-entrypoint) (/api-entrypoint/addUser). ✓")
    print("\033[92mRunning Flask APP Server in: localhost:9999. ✓\033[0m")
    logging.info("Running Flask APP Server in: localhost:9999. ✓")
    # finally run the app on localhost:9999
    flask_app.run(host = "0.0.0.0", port = 9999)
    return 0  # when app is shutdown returns 0


if __name__ == '__main__':  # when file is being launched run the main function
    main()
