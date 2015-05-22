from django.shortcuts import render
from django.http import HttpResponseForbidden, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from slack import utils
from django.core.files.storage import default_storage

from goodreads import client
from goodreads.session import GoodreadsSession
gc = client.GoodreadsClient(settings.GOODREADS_KEY, settings.GOODREADS_SECRET)

import os
import json


def write_token_data(token_info):
	try:
		f = default_storage.open('goodreads.json', 'w')
		f.write(json.dumps(token_info))
		f.close()
	except IOError:
		self._warn("Couldn't write token cache to goodreads.json")
		pass

def read_token_data():
	token_info = None
	try:
		f = default_storage.open('goodreads.json', 'r')
		token_info_string = f.read()
		f.close()
		token_info = json.loads(token_info_string)
	except IOError:
		self._warn("Couldn't read token data")
	return token_info


def authorise(request):
	gc.session = GoodreadsSession(settings.GOODREADS_KEY, 
		settings.GOODREADS_SECRET, 
		access_token=None, 
		access_token_secret=None)
	auth_url = gc.oauth_init()
	url = auth_url + "&oauth_callback="+settings.GOODREADS_REDIRECT_URI
	return redirect(url)

def callback(request):
	gc.session.session = gc.session.oauth_finalize()
	details = {
		'access_token':gc.session.session.access_token, 
		'access_token_secret':gc.session.session.access_token_secret
	}
	write_token_data(details)
	return HttpResponse("Authorized!")

# @require_http_methods(["POST"])
@csrf_exempt
def index(request):
	if request.POST.get('token') != settings.LIBRARY_SLACK_TOKEN:
		return HttpResponseForbidden()

	token_data = read_token_data()
	if not token_data:
		return HttpResponse("Unable to get token - is goodreads authorized?")

	gc.session.access_token = token_data['access_token']
	gc.session.access_token_secret = token_data['access_token_secret']
	gc.session.oauth_resume()


	# Items are keyed by ISBN, with a number to refer to how many copies are available.
	username = request.POST.get('user_name')
	channel = request.POST.get('channel_name')
	text = request.POST.get('text', '')
	usage = "Library:\n /l list - show available books\n"
	response = usage
	ignored_shelves = ['read', 'currently-reading', 'to-read', 'hcibay']
	if text != '':
		bits = text.split(' ', 1)
		if len(bits) == 1:
			if text == 'list':
				user = gc.user(settings.GOODREADS_USERID)
				shelves = user.shelves()
				shelf_list = []
				for shelf in shelves:
					if shelf['name'] not in ignored_shelves:
						shelf_list.append(shelf['name'])
				shelf_list.sort()
				response = ""
				for shelf_name in shelf_list:
					response += "Books with @"+shelf_name+":\n"
					resp = gc.request("review/list.xml", {'page':1,'format':'xml', 'id':settings.GOODREADS_USERID, 'shelf':shelf_name})
					books = resp['books']['book']
					for book in books:
						response += "*"+book['title']+" - "+book['authors']['author']['name']+"* ("+book['isbn']+")\n"
				
	return HttpResponse(response)