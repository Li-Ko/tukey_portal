from django.core import urlresolvers
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.http import urlencode
from horizon.decorators import require_auth

from .forms import OsdcQueryForm
from .forms import QueryFields

@require_auth
def query_builder(request):
    ''' Main view displays the running query and allows the user to run an
    instance from here '''

    # Create a form from the current query string as so
    # the required fields are "query_name" and "cloud" and they have a fixed
    # name structure we could also add additional fields with fixed names as
    # we need.
    # The query up to this point is represented by the query string as
    # follows: num_field=value
    # for example: ?0_disease_abbr=BRCA&1_=AND&2_sample_id=231*
    # or something like that

    if request.method == 'POST':
        data = request.POST
    if request.method == 'GET':
        data = request.GET

    print data

    form = OsdcQueryForm(data)

#    print "form ", form

    return render(request, 'osdcquery/form.html', {
        'form': form,
        'query_fields': QueryFields()
    })

#
#
#    if request.method == 'POST': # If the form has been submitted...
#        print request.POST
#        form = OsdcQueryForm(request.POST) # A form bound to the POST data
#        if form.is_valid(): # All validation rules pass
#            # Process the data in form.cleaned_data
#            #...
#            ignore = ['csrfmiddlewaretoken', 'cloud']
#
#            #pop this so it wont show up in the stuff
#            cloud = request.POST["cloud"]
#
#            rest_url = "?".join([urlresolvers.reverse(
#                "horizon:project:instances:launch"),
#                urlencode(
#                    {"cloud": cloud.capitalize(),
#                    "customization_script": " AND ".join([
#                        "%s:%s" % (attr, request.POST[attr]) for attr
#                        in request.POST if attr not in ignore and
#                        request.POST[attr] != ''])})])
#
#            return HttpResponseRedirect(rest_url)
#
#    else:
#        print request.GET
#        form = OsdcQueryForm(request.GET)
#        form.set_cloud(request.user)
#
#    return render(request, 'osdcquery/form.html', {
#        'form': form,
#    })
#

@require_auth
def select_field(request):
    ''' This is the view for the dialog where a user selects a new field to
    add to the query'''

    return render(request, 'osdcquery/select.html', {
        'query_fields': QueryFields()
    })



#def query(request):
#    #return HttpResponse(request.POST['choice'])
#
#    q_str = ''
#    for attr in request.POST:
#        q_str += attr + ":" + request.POST[attr]
#
#    #return HttpResponse(q_str)
#    return HttpResponse("The post : " +str(request.POST))
