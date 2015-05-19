from django.http import HttpResponseForbidden, HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def bookmark(request):
	return HttpResponse("Done!")