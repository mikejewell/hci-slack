from django.http import HttpResponseForbidden, HttpResponse
import json

def bookmark(request):
	return HttpResponse("Done!")