# Create your views here.
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.views.decorators.csrf import csrf_exempt

import urllib2, json
from revproxy import proxy

@csrf_exempt
def reverse_proxy(request, ip, path):
    request.path = path
    return proxy.proxy_request(request, destination="http://%s" % ip)

