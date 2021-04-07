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
import sys
sys.dont_write_bytecode = True  # not create a __pycache__ folder
from oms import oreMinutiSecondi


def queryAPI(service, youtube_api_key, cache, playlist_ID):
    """Core of this program, this function analyze the playlist and save the results of the operation in the Cache System

    :param service: the loaded json file for querying the google API
    :param youtube_api_key: my api key, from google developer console
    :param cache: Redis cache system
    :param playlist_ID: ID of the playlist to be analyzed

    :type service: json
    :type youtube_api_key: String
    :type cache: Redis Object
    :type playlist_ID: String

    :return: (json) json response: {'message': 'Success','tempoIMP': time_spent,'durata': playlist_duration,'counter': video_counter}
    """
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
    return response  # return the response
