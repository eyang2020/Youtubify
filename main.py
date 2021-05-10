import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from googleapiclient.discovery import build
from pprint import pprint

SPOTIFY_CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
SPOTIFY_CLIENT_SECRET = os.environ['SPOTIFY_CLIENT_SECRET']
YOUTUBE_API_KEY = os.environ['YOUTUBE_API_KEY']
#CLIENT_SECRET_FILE = 'client_secret.json'
#SCOPES = ['https://www.googleapis.com/auth/youtube']

sp = spotipy.Spotify (
    auth_manager=SpotifyClientCredentials (
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    )
)

youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# spotify
def getTracksByArtist(artist_name):
    results = sp.search(q=artist_name, limit=10)
    for idx, track in enumerate(results['tracks']['items']):
        print(idx, track['name'])

# spotify
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

# spotify
def getTrackId(track_name):
    result = sp.search(q=track_name, type="track", limit=1, offset=0, market='US')
    if result['tracks']['items']:
        print(f"track id: {result['tracks']['items'][0]['id']}")

# youtube
def getYoutubeVideo(keyword):
    #Example: search for youtube videos using a keyword
    request = youtube.search().list(
        q='nyanpasu',
        part='snippet',
        type='video',
        maxResults='1'
    )
    response = request.execute()
    #pprint(response)
    for item in response['items']:
        print(item['snippet'])

# youtube
def createYoutubePlaylist():
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
    pprint(response)

# make sure playlist is public/unlisted
# youtube
def parseYoutubePlaylist(playlist_id):
    # given the playlist id of a youtube playlist
    # returns a list of song/video titles
    request = youtube.playlistItems().list(
        part='snippet',
        playlistId=playlist_id,
        maxResults=50
    )
    response = request.execute()

    # get first batch
    playlistItems = response['items']
    nextPageToken = response.get('nextPageToken')
    while nextPageToken:
        request = youtube.playlistItems().list(
            part='snippet',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=nextPageToken
        )
        response = request.execute()
        playlistItems.extend(response['items'])
        nextPageToken = response.get('nextPageToken')

    titles = []

    idx = 1
    for item in playlistItems:
        #print(f"{idx}. {item['snippet']['title']}")
        titles.append(item['snippet']['title'])
        idx += 1

    return titles

# playground
print("Running tests...")
titles = parseYoutubePlaylist('PLwUNvBOxUWrGnpvKYuK8R1CxXbSBSfa4n')
for title in titles:
    print(title)
    getTrackId(title)

# notes
# https://github.com/plamere/spotipy/blob/master/examples/create_playlist.py
# creates a playlist, deletes it after 24 hours?
# https://www.youtube.com/watch?v=86YgnJMDrfk
# error handling: check if youtube video is private, or spotify song is greyed-out
# https://developers.google.com/youtube/v3/code_samples/code_snippets?apix=true
# first work on youtube -> spotify
