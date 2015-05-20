from django.http import HttpResponseForbidden, HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect
from django.conf import settings

from spotipy.oauth2 import SpotifyOAuth
import spotipy

auth = SpotifyOAuth(
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
			response = "Added track: *"+track['name']+" ("+artist['name']+")*"
	else:
		response = "Couldn't get token - maybe try authorizing again."
	return HttpResponse(response)

def authorise(request):
	url = auth.get_authorize_url()
	return redirect(url)

def callback(request):
	code = request.GET.get('code')
	state = request.GET.get('state')
	token = auth.get_access_token(code)
	return HttpResponse("Authorized!")
