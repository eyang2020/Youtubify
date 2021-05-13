import os
import re
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from googleapiclient.discovery import build
import youtube_dl
import time

SPOTIPY_CLIENT_ID = os.environ['SPOTIPY_CLIENT_ID']
SPOTIPY_CLIENT_SECRET = os.environ['SPOTIPY_CLIENT_SECRET']
YOUTUBE_API_KEY = os.environ['YOUTUBE_API_KEY']
#CLIENT_SECRET_FILE = 'client_secret.json'
#SCOPES = ['https://www.googleapis.com/auth/youtube']

sp = spotipy.Spotify (
    auth_manager=SpotifyClientCredentials (
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET
    )
)

youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
ydl = youtube_dl.YoutubeDL(
    {
        'quiet': True,
        'ignoreerrors': True
    }
)

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
def getTrackId(query):
    markets = ['US', 'JP']
    for market in markets:
        result = sp.search(q=query, type="track", limit=1, offset=0, market=market)
        if result['tracks']['items']:
            return result['tracks']['items'][0]['id']
    return -1

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

def clean(s):
    # clean a string 's' into a spotify search query
    # remove nonalpha chars
    s = ' '.join(w for w in re.split(r'\W', s) if w)
    s = s.lower()
    # remove any whole keywords
    keywords = ['mv', 'music video', 'ft', 'ft.', 'feat', 'feat.']
    pat = re.compile(r'\b(?:{})\b'.format('|'.join(keywords)))
    return pat.sub('', s)

# make sure playlist is public/unlisted
# youtube
def parseYoutubePlaylist(playlist_id):
    # given the playlist id of a youtube playlist
    # returns a list of corresponding track ids on spotify
    # get playlist title, playlist size (# of videos)
    request = youtube.playlists().list(
        part='snippet, contentDetails',
        id=playlist_id,
    )
    response = request.execute()
    playlistTitle = response['items'][0]['snippet']['title']
    playlistVideoCnt = response['items'][0]['contentDetails']['itemCount']
    print(f'Playlist Title: {playlistTitle}')
    print(f'Video count: {playlistVideoCnt}')
    # limit playlist size to 500 videos.
    if playlistVideoCnt > 500:
        return -1
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

    foundTrackIds = []

    idx = 1
    for item in playlistItems:
        #todo: change playlistItems to already contain the videoId and title of non private/deleted videos
        videoTitle = item['snippet']['title']
        if videoTitle == 'Private video' or videoTitle == 'Deleted video': continue
        #todo: deal with unavailable videos / region blocked
        videoId = item['snippet']['resourceId']['videoId']
        videoUrl = f'http://www.youtube.com/watch?v={videoId}'
        print(f'{idx}. {videoTitle}')
        try:
            with ydl: video = ydl.extract_info(videoUrl, download=False)
            try: 
                videoArtist = clean(video['artist'])
                videoTrack = clean(video['track'])
                # search for this track on spotify
                query = videoArtist + ' ' + videoTrack
                print(f'query: {query}')
                trackId = getTrackId(query)
                if trackId != -1:
                    foundTrackIds.append(trackId)
                    print(f'{idx}. https://open.spotify.com/track/{trackId}')
            except KeyError:
                # must use video title
                videoTitle = clean(videoTitle)
                print(f'cleaned title: {videoTitle}')
                # search for this track on spotify
                trackId = getTrackId(videoTitle)
                if trackId != -1: 
                    foundTrackIds.append(trackId)
                    print(f'{idx}. https://open.spotify.com/track/{trackId}')
            idx += 1
            time.sleep(1)
        except Exception as e:
            #print(e)
            pass
    return (playlistTitle, foundTrackIds)

# playground
'''
print('Running tests...')
foundTrackIds = parseYoutubePlaylist('PLwUNvBOxUWrEQNZTv-uCCC5ngUw2YIEn-')
idx = 1
for trackId in foundTrackIds:
    # add track ids to a playlist in spotify
    #print(f'trackId: {trackId}')
    print(f'{idx}. https://open.spotify.com/track/{trackId}')
    idx += 1
'''

# error handling: check if youtube video is private, or spotify song is greyed-out
# first work on youtube -> spotify
# spotify playlist name can be 100 chars (including spaces)
# youtube playlist name can be ? chars (including spaces)
# todo: make a Video class with attributes: title, id. url can be derived from id.
