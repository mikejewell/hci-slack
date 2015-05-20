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
	usage = "Usage: /link <key> - get a link\n/link list - show available links\n/link <key> <url> - create a new link\n/link rm <key> - remove a link"
	response = usage
	if text != '':
		bits = text.split(' ')
		if len(bits) == 1:
			if text == 'list':
				keys = redis.hkeys('links')
				keys.sort()
				response = 'Links available: '+', '.join(keys)
			else:
				response = '<'+redis.hget('links', bits[0])+'>'
				if response == None:
					response = "Link does not exist."
		elif len(bits) == 2:
			if bits[0] == 'rm':
				redis.hdel('links', bits[1])
				response = "Removed link: "+bits[1]
			else:
				redis.hset('links', bits[0], bits[1])
				response = 'Have set '+bits[0]+' to link to '+bits[1]

	return HttpResponse(response)