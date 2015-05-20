from django.http import HttpResponseForbidden, HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from slack import utils

import os
import redis

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
redis = redis.from_url(redis_url)


@require_http_methods(["POST"])
@csrf_exempt
def index(request):
	if request.POST.get('token') != settings.HELP_SLACK_TOKEN:
		return HttpResponseForbidden()

	text = request.POST.get('text', '')
	usage = "Help Entries:\n /h <key> - look up a help entry\n/h list - show available help entries\n/h <key> <text> - create a new help entry\n/h rm <key> - remove a help entry"
	response = usage
	if text != '':
		bits = text.split(' ', 1)
		if len(bits) == 1:
			if text == 'list':
				keys = redis.hkeys('help')
				keys.sort()
				formatted_keys = ["*"+x+"*" for x in keys]
				response = 'Entries available: '+', '.join(formatted_keys)
			else:
				entry = redis.hget('help', bits[0])
				if entry == None:
					response = "Entry does not exist."
				else:
					response = "```"+entry+"```"
		elif len(bits) == 2:
			if bits[0] == 'rm':
				redis.hdel('help', bits[1])
				response = "Removed entry: *"+bits[1]+"*"
			else:
				if bits[0] != 'rm' and bits[0] != 'list':
					redis.hset('help', bits[0], bits[1])
					response = 'Have set *'+bits[0]+'* to show ```'+bits[1]+'```'
					utils.send_message("@"+username+" added *"+bits[0]+"* to show ```"+bits[1]+"```", 
						channel="#general",
					)

	return HttpResponse(response)