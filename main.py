import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from googleapiclient.discovery import build
from pprint import pprint

SPOTIFY_CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
SPOTIFY_CLIENT_SECRET = os.environ['SPOTIFY_CLIENT_SECRET']
YOUTUBE_API_KEY = os.environ['YOUTUBE_API_KEY']
CLIENT_SECRET_FILE = 'client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/youtube']

sp = spotipy.Spotify (
    auth_manager=SpotifyClientCredentials (
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    )
)

youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

def getTracksByArtist(artist_name):
    results = sp.search(q=artist_name, limit=10)
    for idx, track in enumerate(results['tracks']['items']):
        print(idx, track['name'])

def getTracksInPlaylist(playlist_id):
    #Example: get the track id's of all tracks in a playlist of id spotify:playlist:{playlist-id}
    pl_id = f'spotify:playlist:{playlist_id}'
    offset = 0
    max_tracks_per_call = 50
    tids = [] # a list of track id's

    while True:
        response = sp.playlist_items(
            pl_id,
            offset=offset,
            fields='items.track.id,total',
            additional_types=['track']
        )
    
        if len(response['items']) == 0:
            break
        
        #pprint(response['items'])
        offset = offset + len(response['items'])
        #print(offset, "/", response['total'])

        for d in response['items']:
            #print(d['track']['id'])
            tids.append(d['track']['id'])

    for start in range(0, len(tids), max_tracks_per_call):
        results = sp.tracks(tids[start: start + max_tracks_per_call])
        for track in results['tracks']:
            print(track['name'] + ' - ' + track['artists'][0]['name'])

#getTracksInPlaylist('1XgFXCIwDTLIavPjiXintl')


#Example: search for youtube videos using a keyword
request = youtube.search().list(
    q='xqc',
    part='snippet',
    type='video',
    maxResults='1'
)
response = request.execute()
#pprint(response)
for item in response['items']:
    print(item['snippet'])

'''
request = youtube.playlists().insert(
    part="snippet,status",
    body={
        "snippet": {
        "title": "Sample playlist created via API",
        "description": "This is a sample playlist description.",
        "tags": [
            "sample playlist",
            "API call"
        ],
        "defaultLanguage": "en"
        },
        "status": {
        "privacyStatus": "public"
        }
    }
)
response = request.execute()

print(response)
'''

# https://github.com/plamere/spotipy/blob/master/examples/create_playlist.py
# creates a playlist, deletes it after 24 hours?
# https://www.youtube.com/watch?v=86YgnJMDrfk
# error handling: check if youtube video is private, or spotify song is greyed-out
# https://developers.google.com/youtube/v3/code_samples/code_snippets?apix=true
