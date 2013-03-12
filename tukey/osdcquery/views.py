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

    if request.method == 'POST':
        form = OsdcQueryForm(request.POST)
	data = request.POST
    if request.method == 'GET':
        form = OsdcQueryForm()
	data = request.GET

    print "and the user is ", request.user
    form.set_cloud(request.user)

    print form.base_fields['cloud'].choices
    print form.fields
    print form.fields['cloud']

    if request.method == 'POST': # If the form has been submitted...
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            #...

            cloud = request.POST["cloud"]

            rest_url = "?".join([urlresolvers.reverse(
                "horizon:project:instances:launch"),
                urlencode(
                    #{"cloud": cloud.capitalize(),
                    {"cloud": cloud.upper(),
                    "customization_script": ('''#!/bin/bash
sudo apt-get update
sudo apt-get install git -y
export http_proxy="http://cloud-controller:3128"
export https_proxy="http://cloud-controller:3128"
cd /tmp
git clone https://github.com/LabAdvComp/osdcquery.git /tmp/temp-osdcquery
sudo dpkg -i /tmp/temp-osdcquery/python-osdcquery_0.1.6dev-1_all.deb
echo "export no_proxy=172.16.1.3,$no_proxy" >> ~/.bashrc
export no_proxy=172.16.1.3,$no_proxy
python -m osdcquery.osdcquery %s '%s' ''') % (data["query_name"],
                    data["generated_query"])})])

            return HttpResponseRedirect(rest_url)

    return render(request, 'osdcquery/form.html', {
        'form': form,
        'query_fields': QueryFields()
    })

