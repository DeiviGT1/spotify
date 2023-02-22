from flask import Flask, request, redirect, session, url_for, render_template, render_template_string
import requests
from flask_cors import CORS
import random
import string
import spotipy.util as util
import spotipy
import urllib
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import re
import urllib.parse
from urllib.parse import urlparse

app = Flask(__name__, template_folder="public")

client_id = 'ef1e8c8912c448d4b07363dcbfc9987f' 
client_secret = '7063943850764e4294bdb995cf2d7b73'
redirect_uri = 'http://localhost:2000/callback'
stateKey = 'user-library-read'

def generate_random_string(length):
    letters = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for i in range(length))

#create a function to get the hash params from the url
def get_hash_params():
  params = {}
  #get url parsed
  parsed_url = urlparse(request.url)
  #get the query params and split them
  query_params = parsed_url.query.split("&")
  #loop through the query params
  for param in query_params:
    #split the param
    param = param.split('=')
    #add the param to the dictionary
    params[param[0]] = param[1]
  return params

@app.before_request
def before_request():
  cookies = {}
  cookie_header = request.headers.get('Cookie')
  if cookie_header:
    cookies = {cookie.split('=')[0]: cookie.split('=')[1] for cookie in cookie_header.split('; ')}

  # Add parsed cookies to request object
  request.cookies = cookies

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/login')
def login():
  #Acá ingresamos a la página de spotify para que el usuario se loguee
  state = generate_random_string(16)
  session[stateKey] = state
  scope = 'user-library-read'

  #Redirigimos la pagina al callback
  return redirect('https://accounts.spotify.com/authorize?client_id=' + client_id + '&response_type=code&redirect_uri=' + redirect_uri + '&state=' + state + '&scope=' + scope)

@app.route('/callback')
def callback():
  code = request.args.get('code')
  state = request.args.get('state')
  stored_state = session[stateKey]
  
  if state is None or state != stored_state:
    return redirect('/#' + urllib.parse.urlencode({'error': 'state_mismatch'}))
  else:
    session.pop(stateKey, None)
    post_data = {
      'code': code, 
      'redirect_uri': redirect_uri, 
      'grant_type': 'authorization_code',
      "client_id": client_id,
      "client_secret": client_secret,
      "redirect_uri": redirect_uri,
      }
    
    SPOTIFY_TOKEN = 'https://accounts.spotify.com/api/token'
    r = requests.post( SPOTIFY_TOKEN, data=post_data)
    response_data = r.json()
    session['access_token'] = response_data['access_token']
    session['refresh_token'] = response_data['refresh_token']
    session['token_type'] = response_data['token_type']
    session['expires_in'] = response_data['expires_in']


    return redirect('/most_listened_songs')

@app.route('/most_listened_songs')
def most_listened_songs():
  sp_oauth = spotipy.Spotify(auth=session['access_token'])
  results = sp_oauth.current_user_saved_tracks_add()
  # dict_ = {}
  # for i in results['items']:
  #   dict_[i['track']['name']] = i['track']['name']
  return results

@app.route('/refresh_token')
def refresh_tok1en():
  code = request.args.get('code')
  refresh_token = session['refresh_token']
  post_data = {'code': code, 
      'redirect_uri': redirect_uri, 
      'grant_type': 'authorization_code',
      "refresh_token": refresh_token,
      "client_id": client_id,
      "client_secret": client_secret,
      "redirect_uri": redirect_uri,
      }

  auth_response = requests.post('https://accounts.spotify.com/api/token', data=post_data)
  if auth_response.status_code == 200:
    auth_response_data = auth_response.json()
    access_token = auth_response_data['access_token']
    session['access_token'] = access_token
    return access_token
  else:
    return 'Error: unable to refresh token', 400

if __name__ == '__main__':
  app.secret_key = 'super secret key'
  app.run(host="localhost", port=2000, debug=True)

