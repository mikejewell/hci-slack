from django.http import HttpResponseForbidden, HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

import os
import redis

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
redis = redis.from_url(redis_url)


@require_http_methods(["POST"])
@csrf_exempt
def link(request):
	text = request.post.get('text', '')
	usage = "Usage: /link set <key> <url> | get <key> | list"
	if text == '':
		response = usage
	elif text == 'list':
		pass
	else:
		bits = text.split(' ')
		if len(bits) != 2:
			response = usage
		elif bits[0] == 'set':
			redis.hset('links', bits[1], bits[2])
			response = 'Have set '+bits[1]+' to link to '+bits[2]
		elif bits[0] == 'get':
			response = redis.hget('links', bits[1])
			if response == None:
				response = "Link does not exist."

	return HttpResponse(response)