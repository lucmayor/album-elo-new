from typing import Union, ClassVar
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

import requests
import config

# python -m uvicorn main:app --reload
# running stock doesnt play nice

# errors:
# jsonable_encoder isnt nice

app = FastAPI()
all_albums = []
processed = {}

# class Album(BaseModel):
#     album_name: str
#     artist_name: str
#     #elo: ClassVar[int] = 1400
#     album_art: str

class Song(BaseModel):
    song_name: str
    artist_name: str
    album_art: str
    album_name: str
    status: bool

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
    for i in range(int(state.total_albums)):
        album = {}
        album['album_name'] = json['topalbums']['album'][i]['name']
        album['artist_name'] = json['topalbums']['album'][i]['artist']['name']
        album['album_art'] = json['topalbums']['album'][i]['image'][3]['#text']
        all_albums.append(album)

# change to getting first result, return artist, albumart, song, and nowplaying
def process_current(json):
    recent_listening = json['recenttracks']['track'][0]
    current = Song
    current.song_name = recent_listening['name']
    current.artist_name = recent_listening['artist']['#text']
    current.album_art = recent_listening['image'][3]['#text']
    current.album_name = recent_listening['album']['#text']
    rlstring = str(recent_listening)
    if "nowplaying" in rlstring:
        current.status = True
    else:
        current.status = False
    deconstruct = jsonable_encoder(current)
    return deconstruct

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
        state.total_albums = "50"
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
        return all_albums
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
        #return recent.json() this one works
        return process_current(recent.json()) #this one doesnt
    else:
        return None

@app.put("/set_id/{api_key}")
def read_key(key: str):
    state.api_key = key
    return {"api_key": key} #this should probably just be a ping to lfm serv