from django.shortcuts import render
from django.http import HttpResponseForbidden, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from slack import utils

from goodreads import client
gc = client.GoodreadsClient(settings.GOODREADS_KEY, settings.GOODREADS_SECRET)

import os
import redis
import json

def index(request):
	if request.POST.get('token') != settings.LIBRARY_SLACK_TOKEN:
		return HttpResponseForbidden()
	# Items are keyed by ISBN, with a number to refer to how many copies are available.
	username = request.POST.get('user_name')
	channel = request.POST.get('channel_name')
	text = request.POST.get('text', '')
	usage = "Library:\n /l list - show available books\n"
	response = usage
	if text != '':
		bits = text.split(' ', 1)
		if len(bits) == 1:
			if text == 'list':
				resp = gc.request("review/list.xml", {'page':1,'format':'xml', 'id':settings.GOODREADS_USERID, 'shelf':settings.GOODREADS_SHELF})
				books = resp['books']['book']
				response = "Library contents:\n"
				for book in books:
					response += book['title']+" - "+book['authors']['author']['name']+"("+book['isbn']+")\n"
	return HttpResponse(response)