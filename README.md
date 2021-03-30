# PlayList-Length-Service
A Python restFul API  that given a YouTube PlayList link or ID analyze it and and returns its total duration and the number of videos in it.
This API is dockerized, implements a cache system for same videos in different playlists, using Redis.

## Quick Start
- start docker
- run `docker-compose -p youtubeapi_pl up` command and open the `localhost:9999` in the browser. There should be the main web page. If you open the `localhost:9999/addUser` instead, there will be an explanation of how to add users for using the API. Using `PostMan` send POST request as shown below and see the response.
- to see the cache system just run `docker exec -it redisCacheSystem redis-cli`, the API saves the video ID (like `dQw4w9WgXcQ` and its duration in seconds) for exactly 1 minute. To see this run the command: `get dQw4w9WgXcQ`
