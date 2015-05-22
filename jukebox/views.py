from django.http import HttpResponseForbidden, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect
from django.conf import settings
from django.core.files.storage import default_storage

import json

from spotipy.oauth2 import SpotifyOAuth
import spotipy

from slack import utils

class SpotifyOAuthExtended(SpotifyOAuth):
	def get_cached_token(self):
		token_info = None
		try:
			f = default_storage.open('jukebox.json', 'r')
			token_info_string = f.read()
			f.close()
			token_info = json.loads(token_info_string)

			# if scopes don't match, then bail
			if 'scope' not in token_info or self.scope != token_info['scope']:
				return None

			if self._is_token_expired(token_info):
				token_info = self._refresh_access_token(token_info['refresh_token'])

		except IOError:
			pass
		return token_info
    
	def _save_token_info(self, token_info):
		try:
			f = default_storage.open('jukebox.json', 'w')
			f.write(json.dumps(token_info))
			f.close()
		except IOError:
			self._warn("Couldn't write token cache to jukebox.json")
			pass

auth = SpotifyOAuthExtended(
	settings.SPOTIFY_KEY, 
	settings.SPOTIFY_SECRET, 
	settings.SPOTIFY_REDIRECT_URI, 
	scope="playlist-modify-public playlist-modify-private",
	cache_path='/tmp/jukebox.json')

import logging
logger = logging.getLogger('testlogger')

@require_http_methods(["POST"])
@csrf_exempt
def index(request):
	if request.POST.get('token') != settings.JUKEBOX_SLACK_TOKEN:
		return HttpResponseForbidden()
	username = request.POST.get('user_name')
	channel = request.POST.get('channel_name')
	text = request.POST.get('text', '')
	token = auth.get_cached_token()
	if token:
		sp = spotipy.Spotify(auth=token['access_token'])
		sp.trace = False
		search_result = sp.search(text)
		results = search_result['tracks']['items']
		if len(results) == 0:
			response = "Could not find any tracks :("
		else:
			track = results[0]
			artist = track['artists'][0]
			sp.user_playlist_add_tracks(settings.SPOTIFY_USERNAME, settings.SPOTIFY_PLAYLIST_ID, [track['id']])
			url = "https://play.spotify.com/track/"+str(track['id'])
			utils.send_message("@"+username+" added track: *"+track['name']+" ("+artist['name']+")* to the shared playlist (<"+url+">)", 
				channel=settings.SLACK_RANDOM_CHAT,
				username="Jukebox",
				icon_emoji=":radio:" 
				)
			response = "Added track: *"+track['name']+" ("+artist['name']+")*"
	else:
		response = "Couldn't get token - maybe try authorizing again."
	return HttpResponse(response)

@csrf_exempt
def test(request):
	f = open('/tmp/jukebox.json')
	info = f.read()
	f.close()
	return HttpResponse(info)

def authorise(request):
	url = auth.get_authorize_url()
	return redirect(url)

def callback(request):
	code = request.GET.get('code')
	state = request.GET.get('state')
	token = auth.get_access_token(code)
	return HttpResponse("Authorized!")
