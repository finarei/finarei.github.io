import os

from flask import Flask, render_template_string, request, redirect, send_from_directory, session, url_for

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler

from waitress import serve

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY') or os.urandom(64)

# I stored my credentials in environment variables for security. 
client_id = os.environ.get('SPOTIPY_CLIENT_ID')
client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')
redirect_uri = os.environ.get('SPOTIPY_REDIRECT_URI') or (
    f"{os.environ.get('RENDER_EXTERNAL_URL', 'http://127.0.0.1:8080')}/callback"
)

# Scopes define the permissions your application needs. 
# You can adjust these based on your requirements.
# Available options can  be found here: https://developer.spotify.com/documentation/web-api/concepts/scopes
scope = 'user-library-read user-top-read user-read-recently-played'

cache_handler = FlaskSessionCacheHandler(session)
sp_oauth = SpotifyOAuth(
    client_id=client_id, 
    client_secret=client_secret, 
    redirect_uri=redirect_uri, 
    scope=scope, 
    cache_handler=cache_handler,
    show_dialog=True)

sp = Spotify(auth_manager=sp_oauth)

@app.route('/background-image')
def background_image():
    app_directory = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(app_directory, 'BackgroundWrapped.png')

def login_page():
    auth_url = sp_oauth.get_authorize_url()
    return render_template_string('''
        <!doctype html>
        <html>
        <head>
            <style>
                body {
                    min-height: 100vh;
                    margin: 0;
                    display: grid;
                    place-items: center;
                    background-image: url('/background-image');
                    background-size: cover;
                    background-position: center;
                    background-attachment: fixed;
                    color: white;
                    font-family: ui-monospace, 'Cascadia Code', 'Source Code Pro',
                        Menlo, Consolas, 'DejaVu Sans Mono', monospace;
                }
                a { color: white; }
                main { text-align: center; }
                .login-prompt { font-size: 2em; }
                .login-link { font-size: 2.25em; }
                .login-note { font-size: 1em; text-align: center; }
                .login-note a { font-size: 1em; }
            </style>
        </head>
        <body>
            <main>
                <p class="login-prompt">Are you ready to get your wrapped early? ᕙ(  •̀ ᗜ •́  )ᕗ</p>
                <a class="login-link" href="{{ auth_url }}">Log in with Spotify</a><br><br>
                <p class="login-note">
                    For more information about how this program works, check out my
                    <a href="https://github.com/finarei/finarei.github.io"
                       target="_blank" rel="noopener noreferrer">GitHub</a>.
                </p>
            </main>
        </body>
        </html>
    ''', auth_url=auth_url)

@app.route('/')
def home():
    # Prompts the user to log in with Spotify if they are not already logged in
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        return login_page()
    else:
        return render_template_string('''
            <!doctype html>
            <html lang="en">
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body {
                        min-height: 100vh;
                        margin: 0;
                        display: grid;
                        place-items: center;
                        background-image: url('/background-image');
                        background-size: cover;
                        background-position: center;
                        background-attachment: fixed;
                        color: white;
                        font-family: ui-monospace, 'Cascadia Code', 'Source Code Pro',
                            Menlo, Consolas, 'DejaVu Sans Mono', monospace;
                        text-align: center;
                    }
                    main { font-size: 2em; }
                </style>
            </head>
            <body>
                <main>
                    <p>You are already logged in!</p>
                    <p>¯&#92;_(ツ)_/¯</p>
                </main>
                <script>
                    window.addEventListener('pagehide', () => {
                        if (!navigator.sendBeacon('/logout')) {
                            fetch('/logout', { method: 'POST', keepalive: true });
                        }
                    });
                </script>
            </body>
            </html>
        ''')
    return redirect(url_for('get_user_data'))

@app.route('/callback')
def callback():
    # Avoids the issue of a user having to log in again if switch browsers
    sp_oauth.get_access_token(request.args['code'])
    return redirect(url_for('get_user_data'))

@app.route('/get_user_data')
def get_user_data():
    # Ensures the user is logged in before fetching their data
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        return login_page()
    
    # Collects the information from SPotify 
    top_tracks = sp.current_user_top_tracks(limit=10)['items']

    top_artists = sp.current_user_top_artists(limit=10)['items']

    recently_played = sp.current_user_recently_played(limit=10)['items']

    # Renders the user's top tracks, top artists, and recently played tracks in a simple HTML format
    return render_template_string('''
            <h1>Your Early Spotify Wrapped</h1>
            <style>
                body {
                    background-image: url('/background-image');
                    background-size: cover;
                    background-position: center;
                    background-attachment: fixed;
                    color: white;
                    font-family: ui-monospace, 'Cascadia Code', 'Source Code Pro',
                        Menlo, Consolas, 'DejaVu Sans Mono', monospace;
                }
                a { color: white; }
                h1 { margin-top: 1.5em; }
                .top-sections {
                    display: grid;
                    grid-template-columns: repeat(2, minmax(0, 1fr));
                    gap: 1.5em;
                    align-items: start;
                }
                .section-box {
                    min-width: 0;
                    padding: 1em;
                    border-radius: 12px;
                    background: rgba(0, 0, 0, 0.5);
                }
                .section-box .ranked-list li { font-size: 1.1em; }
                .section-box:nth-child(2) .ranked-list li span { font-size: calc(1.1em + 5pt); }
                .recently-played-box {
                    margin-top: 1.5em;
                    padding: 1.5em;
                    border-radius: 12px;
                    background: rgba(0, 0, 0, 0.5);
                }
                .footer-box {
                    margin-top: 1.5em;
                    padding: 1em 1em 2em;
                    border-radius: 12px;
                    background: rgba(0, 0, 0, 0.5);
                    text-align: center;
                }
                .footer-links {
                    display: flex;
                    justify-content: center;
                    flex-wrap: wrap;
                    gap: 1.5em;
                }
                .border-loop {
                    position: relative;
                    width: 100%;
                    height: 2.5em;
                    margin-top: 2em;
                    overflow: hidden;
                }
                .border-loop-track {
                    display: flex;
                    width: max-content;
                    animation: ornament-scroll 20s linear infinite;
                }
                .border-loop-copy {
                    flex: none;
                    white-space: nowrap;
                }
                @keyframes ornament-scroll {
                    to { transform: translateX(-50%); }
                }
                @media (max-width: 700px) {
                    .top-sections { grid-template-columns: 1fr; }
                }
                .ranked-list {
                    list-style: none;
                    padding: 0;
                    counter-reset: rank;
                }
                .ranked-list li {
                    display: grid;
                    grid-template-columns: 2.5em 100px minmax(0, 1fr);
                    align-items: center;
                    column-gap: 0.5em;
                    margin-bottom: 1em;
                }
                .recently-played-list {
                    display: grid;
                    grid-template-columns: repeat(5, minmax(0, 1fr));
                    gap: 1em;
                }
                .recently-played-list li {
                    grid-template-columns: 1.75em 70px minmax(0, 1fr);
                    column-gap: 0.6em;
                    margin-bottom: 0;
                    font-size: 0.95em;
                }
                .recently-played-list li::before { font-size: 1.1em; }
                .recently-played-list .album-cover {
                    width: 70px;
                    height: 70px;
                }
                .ranked-list li::before {
                    counter-increment: rank;
                    content: counter(rank) '.';
                    font-size: 1.25em;
                    font-weight: bold;
                    text-align: right;
                }
                .album-cover {
                    display: block;
                    width: 100px;
                    height: 100px;
                    object-fit: cover;
                }
                @media (max-width: 900px) {
                    .recently-played-list {
                        grid-template-columns: repeat(3, minmax(0, 1fr));
                    }
                }
                @media (max-width: 600px) {
                    .recently-played-list {
                        grid-template-columns: repeat(2, minmax(0, 1fr));
                    }
                }
                @media (max-width: 400px) {
                    .recently-played-list { grid-template-columns: 1fr; }
                }
            </style>
            <div class="top-sections">
                <section class="section-box">
                    <h2>Top tracks</h2>
                    <ol class="ranked-list">
            {% for track in top_tracks %}
                <li>
                {% if track['album']['images'] %}
                    <img class="album-cover"
                         src="{{ track['album']['images'][0]['url'] }}"
                         alt="{{ track['name'] }}">
                {% else %}
                    <span></span>
                {% endif %}
                    <span>
                        {{ track['name'] }}: {{ track['artists'][0]['name'] }}
                        - {{ track['album']['name'] }}<br>
                        <small>Released: {{ track['album']['release_date'] }}</small>
                    </span>
                </li>
            {% else %}
                <li>No top tracks found.</li>
            {% endfor %}
            </ol>
            </section>
                <section class="section-box">
                    <h2>Top artists</h2>
                    <ol class="ranked-list">
            {% for artist in top_artists %}
                <li>
                {% if artist['images'] %}
                    <img class="album-cover"
                         src="{{ artist['images'][0]['url'] }}"
                         alt="{{ artist['name'] }}">
                {% else %}
                    <span></span>
                {% endif %}
                    <span>{{ artist['name'] }}</span>
                </li>
            {% else %}
                <li>No top artists found.</li>
            {% endfor %}
            </ol>
            </section>
            </div>
                <section class="recently-played-box">
                    <h2>Recently played</h2>
                    <ol class="ranked-list recently-played-list">
            {% for item in recently_played %}
                {% set track = item['track'] %}
                <li>
                {% if track['album']['images'] %}
                    <img class="album-cover"
                         src="{{ track['album']['images'][0]['url'] }}"
                         alt="{{ track['name'] }}">
                {% else %}
                    <span></span>
                {% endif %}
                    <span>
                        {{ track['name'] }}: {{ track['artists'][0]['name'] }}<br>
                        <small>Played at: {{ item['played_at'] }}</small>
                    </span>
                </li>
            {% else %}
                <li>No recently played tracks found.</li>
            {% endfor %}
            </ol>
                    <div class="border-loop" aria-hidden="true">
                        <div class="border-loop-track">
                            <span class="border-loop-copy">
                                *ੈ✩‧₊˚༺☆༻*ੈ✩‧₊˚  *ੈ✩‧₊˚༺☆༻*ੈ✩‧₊˚  *ੈ✩‧₊˚༺☆༻*ੈ✩‧₊˚  *ੈ✩‧₊˚༺☆༻*ੈ✩‧₊˚  
                                *ੈ✩‧₊˚༺☆༻*ੈ✩‧₊˚  *ੈ✩‧₊˚༺☆༻*ੈ✩‧₊˚  *ੈ✩‧₊˚༺☆༻*ੈ✩‧₊˚  *ੈ✩‧₊˚༺☆༻*ੈ✩‧₊˚  
                                *ੈ✩‧₊˚༺☆༻*ੈ✩‧₊˚  *ੈ✩‧₊˚༺☆༻*ੈ✩‧₊˚  *ੈ✩‧₊˚༺☆༻*ੈ✩‧₊˚  *ੈ✩‧₊˚༺☆༻*ੈ✩‧₊˚  
                            </span>
                            <span class="border-loop-copy">
                                *ੈ✩‧₊˚༺☆༻*ੈ✩‧₊˚  *ੈ✩‧₊˚༺☆༻*ੈ✩‧₊˚  *ੈ✩‧₊˚༺☆༻*ੈ✩‧₊˚  *ੈ✩‧₊˚༺☆༻*ੈ✩‧₊˚  
                                *ੈ✩‧₊˚༺☆༻*ੈ✩‧₊˚  *ੈ✩‧₊˚༺☆༻*ੈ✩‧₊˚  *ੈ✩‧₊˚༺☆༻*ੈ✩‧₊˚  *ੈ✩‧₊˚༺☆༻*ੈ✩‧₊˚  
                                *ੈ✩‧₊˚༺☆༻*ੈ✩‧₊˚  *ੈ✩‧₊˚༺☆༻*ੈ✩‧₊˚  *ੈ✩‧₊˚༺☆༻*ੈ✩‧₊˚  *ੈ✩‧₊˚༺☆༻*ੈ✩‧₊˚  
                            </span>
                        </div>
                    </div>
            </section>
                <footer class="footer-box">
                    <p>Made by Josefine Reinhardsen</p>
                    <nav class="footer-links">
                        <a href="https://github.com/finarei/finarei.github.io"
                           target="_blank" rel="noopener noreferrer">GitHub</a>
                        <a href="https://www.linkedin.com/in/josefine-reinhardsen/"
                           target="_blank" rel="noopener noreferrer">LinkedIn</a>
                        <a href="https://readymag.website/u2585661847/6323605/"
                           target="_blank" rel="noopener noreferrer">Visual portfolio</a>
                        <a href="https://open.spotify.com/user/31ilwnrcavh53urrop4dp6apuqie?si=u7EUC-GWTn2iOJXgo0d5PA&amp;utm_source=copy-link"
                           target="_blank" rel="noopener noreferrer">Spotify</a>
                    </nav>
                </footer>
                <script>
                    window.addEventListener('pagehide', () => {
                        if (!navigator.sendBeacon('/logout')) {
                            fetch('/logout', { method: 'POST', keepalive: true });
                        }
                    });
                </script>
        ''', top_tracks=top_tracks, top_artists=top_artists, recently_played=recently_played)

@app.route('/logout', methods=['POST'])
def logout():
    # Clears the session and logs the user out
    session.clear()
    return '', 204

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))