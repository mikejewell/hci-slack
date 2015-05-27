from django.shortcuts import render
from django.http import HttpResponseForbidden, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from slack import utils
from django.core.files.storage import default_storage
from django.shortcuts import redirect
from rauth.service import OAuth1Service, OAuth1Session
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
	auth_url = gc.session.oauth_init()
	details1 = {
		'request_token':gc.session.request_token,
		'request_token_secret':gc.session.request_token_secret,
	}
	write_token_data(details1)
	url = auth_url + "&oauth_callback="+settings.GOODREADS_REDIRECT_URI
	return redirect(url)

def callback(request):
	gc.session = GoodreadsSession(settings.GOODREADS_KEY, 
		settings.GOODREADS_SECRET, 
		access_token=None, 
		access_token_secret=None)
	gc.session.service = OAuth1Service(
            consumer_key=settings.GOODREADS_KEY,
            consumer_secret=settings.GOODREADS_SECRET,
            name='goodreads',
            request_token_url='http://www.goodreads.com/oauth/request_token',
            authorize_url='http://www.goodreads.com/oauth/authorize',
            access_token_url='http://www.goodreads.com/oauth/access_token',
            base_url='http://www.goodreads.com/'
        )
	details2 = read_token_data()
	gc.session.request_token = details2['request_token']
	gc.session.request_token_secret = details2['request_token_secret']
	
	gc.session.oauth_finalize()
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

	gc.session = GoodreadsSession(settings.GOODREADS_KEY, 
		settings.GOODREADS_SECRET, 
		access_token=token_data['access_token'], 
		access_token_secret=token_data['access_token_secret'])
	gc.session.access_token = token_data['access_token']
	gc.session.access_token_secret = token_data['access_token_secret']
	gc.session.oauth_resume()


	# Items are keyed by ISBN, with a number to refer to how many copies are available.
	username = request.POST.get('user_name')
	channel = request.POST.get('channel_name')
	text = request.POST.get('text', '')
	usage = "Library:\n /l list - show available books\n /l <isbn> - add a book to your shelf\n /l rm <isbn> - remove a book from your shelf."
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
					if 'book' in resp['books']:
						books = resp['books']['book']
						if type(books) != list:
							books = [books]
						for book in books:
							response += "*"+book['title']+" - "+book['authors']['author']['name']+"* ("+book['isbn']+")\n"
			else:
				book = gc.book(isbn=bits[0])
				if not book:
					response = "Couldn't locate book. Please check the ISBN number!"
				else:
					gc.session.session.get("http://www.goodreads.com/shelf/add_to_shelf.xml", params={'name':username,'book_id':book.gid})
					response = "Added book: "+book.title
		elif len(bits) == 2:
			if bits[0] == 'rm':
				book = gc.book(isbn=bits[1])
				if not book:
					response = "Couldn't locate book. Please check the ISBN number!"
				else:
					gc.session.session.get("http://www.goodreads.com/shelf/add_to_shelf.xml", params={'name':username,'book_id':book.gid,'a':'remove'})
					response = "Removed book: "+book.title
	return HttpResponse(response)