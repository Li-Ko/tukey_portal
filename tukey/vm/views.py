#from django.conf import settings
#from django.shortcuts import render_to_response
#from django.template import RequestContext
#from django.template.defaultfilters import slugify
from django.views.decorators.csrf import csrf_exempt
from horizon.decorators import require_auth
from django.http import Http404

from revproxy import proxy

@require_auth
@csrf_exempt
def reverse_proxy(request, cloud, ip, path):
    request.path = path[-1] if path.endswith("/") else path
    if cloud.lower() == "sullivan":
        return proxy.proxy_request(request, destination="http://%s" % ip)
    raise Http404

