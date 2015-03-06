from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, redirect
from tukey.keyservice.models import Key, Repository
from tukey.keyservice.forms import ARKForm, RepositoryForm, KeyForm
import re
from signpostclient import SignpostClient
import settings
#For now going to assume the prefix are letters and the id is digits... can change later?
#In a lot of ways this is a hack -- needs to play better with the datasets in general.

def keyservice_invalid(request, key):
    print('invalid response')
    return render_to_response('keyservice/invalid.html', {'key' : key}, context_instance=RequestContext(request))

def keyservice(request):
    if request.method == 'POST':
        form = ARKForm(request.POST)
        if form.is_valid():
            ark_key = form.cleaned_data['ark_key']
            url = '/keyservice/' + ark_key
            return HttpResponseRedirect(url)
    else:
        form = ARKForm()

    return render_to_response('keyservice/keyservice_index.html', {'form' : form }, context_instance=RequestContext(request))


def get_signpost():
    return SignpostClient(settings.SIGNPOST_URL,version='v0')

client = get_signpost()
def keyservice_lookup(request, key):
    match = re.search(r'^ark:/(\d+)/', key)
    print('match' + str(match))
    if match:
        naan = match.group(1)
        if naan == "31807":
            subkey = key[match.end(1)+1:]
            print('subkey: ' + str(subkey))
            try:
                doc = client.get(subkey)
                if len(doc.urls)>0:
                    return HttpResponseRedirect(doc.urls[0])
                else:
                    return render_to_response('keyservice/does_not_exist.html', {'key' : key}, context_instance=RequestContext(request))
            except:
                return render_to_response('keyservice/does_not_exist.html', {'key' : key}, context_instance=RequestContext(request))
                    
                
            #return HttpResponse("We are the naan and the key is: " + key + " prefix is: " + prefix + " id is: " + key_id + " from db: " + url)
        else:
            return render_to_response('keyservice/invalid_naan.html', {'naan' : naan}, context_instance=RequestContext(request))

    return render_to_response('keyservice/invalid.html', {'key' : key}, context_instance=RequestContext(request))
    

def add_repository(request):
    if request.user.is_authenticated():
        f = RepositoryForm(request.POST or None)
        if f.is_valid():
            f.save()
            f = RepositoryForm()
            return render_to_response("keyservice/repository_add.html", {'form': f, 'success' : 'Repository Saved'}, context_instance=RequestContext(request))

        return render_to_response("keyservice/repository_add.html", {'form': f}, context_instance=RequestContext(request))
    return redirect("keyservice:keyservice_index")

def add_key(request):
    if request.user.is_authenticated():
        f = KeyForm(request.POST or None)
        if f.is_valid():
            f.save()
            f = KeyForm()
            return render_to_response("keyservice/key_add.html", {'form': f, 'success' : True}, context_instance=RequestContext(request))

        return render_to_response("keyservice/key_add.html", {'form': f}, context_instance=RequestContext(request))
    return redirect("keyservice:keyservice_index")
