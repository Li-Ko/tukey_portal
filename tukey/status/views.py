# Create your views here.
from django.conf import settings
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.template.defaultfilters import slugify

import urllib2, json

def get_percent(used, total):
    if float(total) == 0:
        return 0
    else:
        return float(used)/float(total)

def append_status(data, cloud_status_data, currcloud, label, idprefix, value_name):
    max_val =  data[currcloud][value_name]['max']
    val =  data[currcloud][value_name]['val']
    cloud_status_data.append((label, idprefix + '-' + value_name, val, max_val,
        get_percent(val, max_val)))

def status_public(request):
    return redirect('https://www.opensciencedatacloud.org/status/#Bionimbus-PDC')

def server_down(request):
    return render_to_response("maintenance.html")
