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
	text = request.POST.get('text', '')
	usage = "Usage: /link set <key> <url> | get <key> | list"
	if text == '':
		response = usage
	elif text == 'list':
		keys = redis.hkeys('links')
		keys.sort()
		response = 'Links available: '+','.join(keys)
	else:
		bits = text.split(' ')
		if bits[0] == 'set' and len(bits) == 3:
			redis.hset('links', bits[1], bits[2])
			response = 'Have set '+bits[1]+' to link to '+bits[2]
		elif bits[0] == 'get' and len(bits) == 2:
			response = redis.hget('links', bits[1])
			if response == None:
				response = "Link does not exist."
		else:
			response = usage

	return HttpResponse(response)