from flask import Blueprint, render_template, redirect
from spotify import app_Authorization, user_Authorization, Profile_Data, Playlist_Data, Song_Data
import pandas as pd

# Se crea un objeto Blueprint para definir las rutas asociadas a este módulo.
mod = Blueprint('controllers', __name__, url_prefix='')

# Se define una ruta para la página de inicio de la aplicación.
@mod.route("/")
def index():
    # Authorization
    return render_template("index.html")

@mod.route("/login")
def login():
    # Authorization
    auth_url = app_Authorization()
    return redirect(auth_url)

@mod.route("/callback")
def callback():
    authorization_header = user_Authorization()

    #Gathering of profile data
    profile_data = Profile_Data(authorization_header)
    user_id = profile_data["id"]
    user_name = profile_data["display_name"]

    #Borramos los datods de la base de datos que se encuentren con el mismo user_id
    # # # # # # delete_all_documents({'info.user_id': user_id})
    #Gathering of playlist data
    playlist_data = Playlist_Data(authorization_header,profile_data)

    avg_dicts = []
    final_result = []
    for items in playlist_data["items"]:
        playlist_name = items["name"]
        url = items["tracks"]["href"]
        song_data = Song_Data(authorization_header,url)
        for song in song_data["items"]:

            avg_dicts.append({
                    "id":song["track"]["id"],
                    "name":song["track"]["name"],
                    "artist":song["track"]["artists"][0]["name"],
                    "playlist_name":playlist_name,
                    "added_at":song["added_at"],
                    "user_id":user_id,
                    "user_name":user_name,
                    "duration_ms":song["track"]["duration_ms"],
                    "popularity":song["track"]["popularity"],
                    "explicit":song["track"]["explicit"],
                    "amount_available_markets":len(song["track"]["available_markets"]),
                })
        
        df = pd.DataFrame(avg_dicts)
        avg_per_playlist = df.groupby("playlist_name").mean()["popularity"]

    for column in avg_per_playlist.index:
        final_result.append({"playlist_name":column, "average_popularity":"{:.2f}".format(avg_per_playlist[column])})
    
    return render_template("playlist.html", avg_per_playlist=final_result)

#Quiero la función de datetime que trae la fecha y hora actual
