import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os


if __name__ == "__main__":

    client_credentials_manager = SpotifyClientCredentials(
        client_id=os.environ["SPOTIFY_CLIENT_ID"], client_secret=os.environ["SPOTIFY_CLIENT_SECRET"]
    )

    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    name = "Jeromes Dream"

    results = sp.search(q="artist:" + name, type="artist")

    items = results["artists"]["items"]
    if len(items) > 0:
        artist = items[0]
        print(artist["name"], artist["images"][0]["url"])
