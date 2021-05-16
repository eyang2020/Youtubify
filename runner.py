from spotify_client import SpotifyClient
from youtube_client import YoutubeClient

def run(playlist_id, sp_user_client):
    # for server-side processing
    sp_client = SpotifyClient()
    yt_client = YoutubeClient()

    yt_playlist = yt_client.getPlaylistInfo(playlist_id)
    playlist_title = yt_playlist.title
    videos = yt_client.getVideosFromPlaylist(playlist_id)
    tracks = [] # list of track ids for Spotify

    for video in videos:
        title = video.title
        artist = video.artist
        track = video.track
        trackId = -1
        if artist and track:
            trackId = sp_client.getTrackId('{} {}'.format(artist, track))
        else:
            trackId = sp_client.getTrackId(title)    
        if trackId != -1:
            tracks.append(trackId)
    
    sp_playlist = sp_user_client.user_playlist_create (
        user=sp_user_client.me()['id'],
        name=playlist_title,
        public=False, 
        collaborative=False,
        description=f'A collection of songs from the YouTube playlist {playlist_title}.'
    )
    # add tracks to created playlist
    sp_user_client.user_playlist_add_tracks(sp_user_client.me()['id'], sp_playlist['id'], tracks)

    
