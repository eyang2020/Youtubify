import os
from flask import Flask, session, request, redirect, render_template, url_for, flash
from flask_session import Session
from flask_executor import Executor
import spotipy
import uuid
from runner import run

app = Flask(__name__)
executor = Executor(app)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)

caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)

def session_cache_path():
    return caches_folder + session.get('uuid')

@app.route('/')
def index():
    if not session.get('uuid'):
        # Step 1. Visitor is unknown, give random ID
        session['uuid'] = str(uuid.uuid4())

    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(
        scope='playlist-modify-public playlist-modify-private',
        cache_handler=cache_handler, 
        show_dialog=True
    )

    if request.args.get("code"):
        # Step 3. Being redirected from Spotify auth page
        auth_manager.get_access_token(request.args.get("code"))
        return redirect('/')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 2. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return render_template('signin.html', auth_url=auth_url)
    
    # Step 4. Signed in, display data
    sp = spotipy.Spotify(auth_manager=auth_manager)
    return render_template('index.html', username=sp.me()['display_name'])

@app.route('/sign_out')
def sign_out():
    try:
        # Remove the CACHE file (.cache-test) so that a new user can authorize.
        os.remove(session_cache_path())
        session.clear()
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))
    return redirect('/')

@app.route('/post_playlist_url', methods=['GET', 'POST'])
def getYouTubePlaylistUrl():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    sp = spotipy.Spotify(auth_manager=auth_manager)
    
    if request.method == 'GET':
        return render_template('loading.html')

    # POST request
    if request.method == 'POST':
        ytPlaylistUrl = request.form['playlist_url_textbox']
        try:
            ytPlaylistId = ytPlaylistUrl.split('list=')[1]
            executor.submit(run, ytPlaylistId, sp)
        except:
            flash("Please insert Valid Youtube Playlist URL", "warning")
            return redirect(url_for('index'))
        # send GET request to render loading.html
        return redirect(url_for('getYouTubePlaylistUrl'))

if __name__ == '__main__':
    app.run(threaded=True, debug=True, host="0.0.0.0", port=5000)

# todo: add recaptcha