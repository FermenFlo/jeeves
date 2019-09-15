from abc import ABC, abstractmethod
import os
import spotipy
import spotipy.util as util
from jeeves.src.commands.utils import APIRequest



# class Spotify


class SpotifyRequest(APIRequest):

    def __init__(self, username = os.environ['SPOTIFY_USERNAME'],
                 client_id=os.environ['SPOTIFY_CLIENT_ID'], client_secret=os.environ['SPOTIFY_CLIENT_SECRET']):
        self.username = username
        self.client_id = client_id
        self.client_secret = client_secret

        client_credentials_manager = spotipy.oauth2.SpotifyClientCredentials(client_id=self.client_id, client_secret=self.client_secret)
        self.sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)


    def search_artists(self, query, n = 10):
        """Input is the name of a desired artist. The output is a dict with the following format, sorted by popularity:
        `   
        {
            'name': name of track,
            'artist': name of primary artist of track,
            'uri': uri for unique track
        }"""
        results = self.sp.search(q='artist:' + query, type='artist', limit = n)
        artists = results['artists']['items']
        sorted_artist_dicts = sorted(artists, key = lambda x: -x['popularity'])
        sorted_artists = [{
            'name': x['name'],
            'uri': x['uri']
            } for x in sorted_artist_dicts]

        return sorted_artists

    def search_tracks(self, query, n = 10):
        """ Input is the name of a desired track. The output is a dict with the following format, sorted by popularity:
        `   
        {
            'name': name of track,
            'artist': name of primary artist of track,
            'uri': uri for unique track
        }
            """
        results = self.sp.search(q='track:' + query , type='track', limit = n)
        tracks = results['tracks']['items']
        sorted_track_dicts = sorted(tracks, key = lambda x: -x['popularity'])
        sorted_tracks = [{
            'name': x['name'],
            'artist': x['artists'][0]['name'],
            'uri': x['uri']
            } for x in sorted_track_dicts]

        return sorted_tracks

    
    def start_playback(self):
        self.sp.start_playback(device_id=None)



if __name__ == '__main__':
    from pprint import pprint
    sr = SpotifyRequest()
    pprint(sr.search_tracks("lounge act"))


#figure out how to add username to config and then figure out scoping and then write methods for all use cases. god damn fuck this package.
# pip install git+https://github.com/plamere/spotipy.git --upgrade