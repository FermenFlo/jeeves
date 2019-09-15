from jeeves.src.commands.commands import Command
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import pprint




if __name__ == '__main__':

    print('running')



    client_credentials_manager = SpotifyClientCredentials(client_id=os.environ['SPOTIFY_CLIENT_ID'],
                                                      client_secret=os.environ['SPOTIFY_CLIENT_SECRET'])

    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


    name = 'Jeromes Dream'

    results = sp.search(q='artist:' + name, type='artist')
    pprint.pprint(results)

    items = results['artists']['items']
    print(len(items))
    if len(items) > 0:
        artist = items[0]
        print(artist['name'], artist['images'][0]['url'])