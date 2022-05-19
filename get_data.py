# Import library
from spotipy.oauth2 import SpotifyOAuth
import yaml
import spotipy
import requests
import pandas as pd
import numpy as np
import json
from tqdm import tqdm
import base64
from requests.exceptions import ReadTimeout
import csv
import datetime

# IDs Andrea
client_id = "fc9749424e5844aaa307f4c00aabb685"
client_secret = "8a05f210615341019d03437d20b6fcbd"

#with open("spotify/spotify_details.yml", 'r') as stream:
#    spotify_details = yaml.safe_load(stream)

# https://developer.spotify.com/web-api/using-scopes/
scope = "user-library-read user-follow-read user-top-read playlist-read-private"


sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="fc9749424e5844aaa307f4c00aabb685",
    client_secret="8a05f210615341019d03437d20b6fcbd",
    redirect_uri="http://localhost:8080/callback/",
    scope=scope,
))

headers = {}
client_creds = f"{client_id}:{client_secret}"
client_creds_base64 = base64.b64encode(client_creds.encode())
token_url = 'https://accounts.spotify.com/api/token'
token_data = {"grant_type": "client_credentials"}
token_headers = {"Authorization": f"Basic {client_creds_base64.decode()}"}


################### GET TOKEN ###################
def get_new_token():
    r = requests.post(token_url, headers=token_headers, data=token_data)
    valid_request = r.status_code in range(200, 299)

    if valid_request:
        r = r.json()
        access_token = r['access_token']
        expires_in = r["expires_in"]    # in second
        # print(access_token, expires_in)

        now = datetime.datetime.now()
        expires = now + datetime.timedelta(seconds=expires_in)
        # did_expire = expires < now

        # Construct Spotify API query
        headers = {
            'Authorization': 'Bearer ' + access_token,
            'Content-type': 'application/json',
        }
    return expires, headers


expires, headers = get_new_token()

def get_all_playlist_df(playlists):
    """
    Get all (non-limited) tracks from a Spotify playlist API call
    :param sp:
    :param sp_call:
    :param sp: Spotify OAuth
    :param sp_call: API function all
    :return: list of tracks
    """
    playlist_data, data = playlists['items'], []
    playlist_ids, playlist_names, num_playlist_tracks = [], [], []
    tot_list = []

    for playlist in playlist_data:

        playlist_ids.append(playlist['id'])
        playlist_names.append(playlist['name'])
        num_playlist_tracks.append(playlist['tracks']['total'])
            
        tracks_playlist_url = "https://api.spotify.com/v1/playlists/"+playlist['id']+"/tracks"
        tracks_list = requests.get(tracks_playlist_url, headers=headers).json()

        #tracks_list = sp.playlist(playlist['id'])

        lst = []
        for track in tracks_list["items"]:
            lst.append(track["track"]["id"])

        tot_list += [lst]


    tracks_df = pd.DataFrame()
    # Playlists
    tracks_df['playlist_id'] = playlist_ids
    tracks_df['playlist_name'] = playlist_names
    tracks_df['num_playlist_tracks'] = num_playlist_tracks
    tracks_df["tracks_id"] = tot_list
        
                    
    return tracks_df

playlist_url = "https://api.spotify.com/v1/users/11128976255/playlists?offset=0&limit=20"
tracks_list = requests.get(playlist_url, headers=headers).json()


track = get_all_playlist_df(tracks_list)
#track = get_all_playlist_df(sp.current_user_playlists())  # limit of 50 playlists by default
print(track.head)
track.to_csv("playlists.csv")




def get_all_tracks(df):
    list_of_track_audio_features = []
    for i,lst in enumerate(df["tracks_id"]):
        for track in lst:

            try:
                track_info_url = "https://api.spotify.com/v1/tracks/" + track
                track_info = requests.get(track_info_url, headers=headers)
                track_audio_analysis_url = "https://api.spotify.com/v1/audio-analysis/" + track
                track_audio_analysis = requests.get(track_audio_analysis_url, headers=headers)
                features_url = "https://api.spotify.com/v1/audio-features/" + track
                features = requests.get(features_url, headers=headers)

                valid_request_1 = track_info.status_code in range(200, 299)
                valid_request_2 = track_audio_analysis.status_code in range(200, 299)
                valid_request_3 = features.status_code in range(200, 299)

                if (valid_request_1 and valid_request_2 and valid_request_3):
                    track_info = track_info.json()
                    track_audio_analysis = track_audio_analysis.json()
                    features = features.json()
                else:
                    print("\n STATUS:", track_info.status_code,
                        track_audio_analysis.status_code, features.status_code)
                    continue
            except Exception as e:
                print(e)
                continue

            track_name = track_info["name"]
            track_explicit = track_info['explicit']
            track_popularity = track_info["popularity"]
            album_info = track_info['album']
            album_name = album_info['name']
            album_release_date = album_info['release_date']
            album_release_date_precision = album_info['release_date_precision']
            artist_info = track_info['artists'][0]
            artist_name = artist_info['name']
            track_info = [track_name, track_explicit, track_popularity,
                        album_name, album_release_date, album_release_date_precision,
                        artist_name]

            #Add in some Spotify Audio Analysis Vectors
            num_seg = 0
            pitches = np.zeros(12)
            timbre = np.zeros(12)
            if "segments" in track_audio_analysis:
                for _, j in enumerate(track_audio_analysis['segments']):
                    pitches += np.array(j['pitches'])
                    timbre += np.array(j['timbre'])
                    num_seg += 1
            track_features_avg_pitches = list(pitches/num_seg)
            track_features_avg_timbre = list(timbre/num_seg)
            track_audio_analysis_list = [
                track_features_avg_pitches, track_features_avg_timbre]

            # Get audio features for this specific track
            features_list = [features['acousticness'], features['danceability'], features['duration_ms'],
                            features['energy'], features['instrumentalness'], features['key'],
                            features['liveness'], features['loudness'], features['mode'],
                            features['speechiness'], features['tempo'], features['time_signature'],
                            features['valence'], features['uri']]

            trackData = [df.loc[i].at["playlist_id"]] + [df.loc[i].at["playlist_name"]] + [track] + track_info + track_audio_analysis_list + features_list

            with open('playlist_dataframe.csv', 'a+', newline='\n') as f:
                # using csv.writer method from CSV package
                write = csv.writer(f)
                write.writerow(trackData)
                f.close()

    return list_of_track_audio_features

columns = ["playlist_id", "playlist_name", "id", "track_name", "track_explicit",  "track_popularity", "album_name", "album_release_date", "album_release_date_precision",
           "artist_name", "audio_avg_pitches", "audio_avg_timbre",
           "audio_acousticness", "audio_danceability", "audio_duration_ms", "audio_energy", "audio_instrumentalness",
           "audio_key_1", "audio_liveness", "audio_loudness", "audio_mode_1", "audio_speechiness", "audio_tempo",
           "audio_time_signature", "audio_valence", "track_uri"]

with open('playlist_dataframe.csv', 'a+', newline='\n') as f:
    # using csv.writer method from CSV package
    write= csv.writer(f)
    write.writerow(columns)
    f.close()

lst = get_all_tracks(track)


