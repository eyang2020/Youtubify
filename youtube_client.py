import os
import re
from googleapiclient.discovery import build
import youtube_dl
import time

YOUTUBE_API_KEY = os.environ['YOUTUBE_API_KEY']
CLIENT_SECRET_FILE = 'client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/youtube']

class Playlist:
    def __init__(self, id, title, video_cnt):
        self.id = id
        self.title = title
        self.video_cnt = video_cnt

class Video:
    def __init__(self, title, track, artist):
        self.title = title
        self.track = track
        self.artist = artist

class YoutubeClient:
    def __init__(self):
        self.yt = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        self.ydl = youtube_dl.YoutubeDL ({
            'quiet': True,
            'ignoreerrors': True#,
            #'source_address': '0.0.0.0'
        })

    @staticmethod
    def clean(s):
        # clean a string 's' into a spotify search query
        # remove nonalpha chars
        s = ' '.join(w for w in re.split(r'\W', s) if w)
        s = s.lower()
        # remove any whole keywords
        keywords = [
            'mv', 
            'music video', 
            'ft', 
            'ft.', 
            'feat', 
            'feat.',
            'official video',
            'official music video',
        ]
        pat = re.compile(r'\b(?:{})\b'.format('|'.join(keywords)))
        return pat.sub('', s)

    def getArtistAndTrackFromVideo(self, video_id):
        url = f"https://www.youtube.com/watch?v={video_id}"
        video = self.ydl.extract_info(url, download=False)
        artist = None
        track = None
        try: 
            artist = self.clean(video['artist'])
            track = self.clean(video['track'])
        except:
            raise ValueError
        if artist and track:
            return (artist, track)
        raise ValueError

    def getPlaylistInfo(self, playlist_id):
        request = self.yt.playlists().list (
            part='snippet, contentDetails',
            id=playlist_id,
        )
        response = request.execute()
        title = response['items'][0]['snippet']['title']
        video_cnt = response['items'][0]['contentDetails']['itemCount']
        return Playlist(playlist_id, title, video_cnt)

    def getVideosFromPlaylist(self, playlist_id):
        videos = []

        def parseVideos(items):
            for item in items:
                title = item['snippet']['title']
                if title == 'Private video' or title == 'Deleted video':
                    continue
                videoId = item['snippet']['resourceId']['videoId']
                try:
                    artist, track = self.getArtistAndTrackFromVideo(videoId)
                    videos.append(Video(title, artist, track))
                except:
                    videos.append(Video(title, None, None))

        request = self.yt.playlistItems().list (
            part='snippet',
            playlistId=playlist_id,
            maxResults=50
        )

        response = request.execute()
        parseVideos(response['items'])
        nextPageToken = response.get('nextPageToken')
    
        while nextPageToken:
            request = self.yt.playlistItems().list(
                part='snippet',
                playlistId=playlist_id,
                maxResults=50,
                pageToken=nextPageToken
            )
            response = request.execute()
            parseVideos(response['items'])
            nextPageToken = response.get('nextPageToken')
            
        return videos
