from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel

import requests
import config

app = FastAPI()
all_albums = []

class Album(BaseModel):
    album_name: str
    artist_name: str
    elo = 1400
    album_art: str

class User(BaseModel):
    api_key: Union[str, None] = None
    username: str
    time_range: str # overall | 7day | 1month | 3month | 6month | 12month
    total_albums: int # The number of results to fetch per page. Defaults to 50.

def lastfm_get(load):
    head = {'user-agent': config.USER_AGENT}
    url = 'https://ws.audioscrobbler.com/2.0/'

    load['api_key'] = config.API_KEY
    load['format'] = 'json'

    return requests.get(url, headers=head, params=load)

def json_process(json):
    albums = json
    for i in range(state.total_albums):
        album = Album
        album.album_name = json['topalbums']['album'][i]['name']
        album.artist_name = json['topalbums']['album'][i]['artist']['name']
        album.album_art = json['topalbums']['album'][i]['image'][3]['#text']
        all_albums.append(album)
    #then add restructuring

# change to getting first result, return artist, albumart, song, and nowplaying
def process_current(json):
    recent_listening = json


# form is [username]?range=[time_range]&albums=[total_albums]
state = User

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/get_albums/{username}")
def read_item(username: str, range: Union[str, None] = None, albums: Union[str, None] = None):
    state.username = username
    if range is None:
        state.time_range = "overall"
    else:
        state.time_range = range
    if albums is None:
        state.total_albums = "100"
    else:
        state.total_albums = albums
    r = lastfm_get({
        'method': 'user.getTopAlbums',
        'user': state.username,
        'period': state.time_range,
        'albums': state.total_albums
    })
    if r.status_code == 200:
        json_process(r.json())
    else:
        return None
    
@app.get("/get_playing/{username}")
def get_playing(username: str):
    state.username = username
    recent = lastfm_get({
        'method': 'user.getRecentTracks',
        'user': state.username
    })
    if recent.status_code == 200:
        # do something
        process_current(recent.json())
    else:
        return None

@app.put("/set_id/{api_key}")
def read_key(key: str):
    state.api_key = key
    return {"api_key": key} #this should probably just be a ping to lfm serv