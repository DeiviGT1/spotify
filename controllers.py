from flask import Blueprint, render_template, redirect
import pandas as pd
from data import delete_all_documents, analyze_average_popularity_per_album, Mongo_Song_Data, Mongo_song_insert_one, delete_count
from spotify import app_Authorization, user_Authorization, Profile_Data, Playlist_Data, Song_Data
import datetime
from pymongo import MongoClient

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
    delete_count()
    #Gathering of playlist data
    playlist_data = Playlist_Data(authorization_header,profile_data)
    x = 0
    dict_tiempos_canciones_cu = {}
    for items in playlist_data["items"]:
        playlist_name = items["name"]
        url = items["tracks"]["href"]
        song_data = Song_Data(authorization_header,url)
        for song in song_data["items"]:
            cancion_1 = playlist_name + "-" + song["track"]["name"] + "1"
            cancion_2 = playlist_name + "-" + song["track"]["name"] + "2"
            cancion_3 = playlist_name + "-" + song["track"]["name"] + "3"
            dict_tiempos_canciones_cu[cancion_1] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f")
            song_to_insert = {
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
                    "time_added":datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f"),
                    "number_song_by_user":x
                }
            x = x + 1
            dict_tiempos_canciones_cu[cancion_2] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f")
            Mongo_song_insert_one(song_to_insert)
            dict_tiempos_canciones_cu[cancion_3] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f")
            
    df_dict_tiempos_canciones_cu = pd.DataFrame(dict_tiempos_canciones_cu.items(), columns=['playlist_name', 'fecha'])
    df_dict_tiempos_canciones_cu.to_csv("tiempos_canciones_cu.csv",index=False)
    avg_per_playlist = analyze_average_popularity_per_album(user_id)
    return render_template("playlist.html", avg_per_playlist=avg_per_playlist)

#Quiero la función de datetime que trae la fecha y hora actual
