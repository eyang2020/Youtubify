import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

SPOTIPY_CLIENT_ID = os.environ['SPOTIPY_CLIENT_ID']
SPOTIPY_CLIENT_SECRET = os.environ['SPOTIPY_CLIENT_SECRET']

class SpotifyClient:
    def __init__(self):
        self.sp = spotipy.Spotify (
            auth_manager=SpotifyClientCredentials (
                client_id=SPOTIPY_CLIENT_ID,
                client_secret=SPOTIPY_CLIENT_SECRET
            )
        )

    def getTrackId(self, query):
        markets = ['US', 'JP']
        for market in markets:
            result = self.sp.search (
                q=query,
                type='track', 
                limit=1, 
                offset=0, 
                market=market
            )
            if result['tracks']['items']:
                return result['tracks']['items'][0]['id']
        return -1
