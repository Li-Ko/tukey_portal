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

    form = OsdcQueryForm(data)
    form.set_cloud(request.user)

    if request.method == 'POST': # If the form has been submitted...
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            #...

            cloud = request.POST["cloud"]

            rest_url = "?".join([urlresolvers.reverse(
                "horizon:project:instances:launch"),
                urlencode(
                    {"cloud": cloud.capitalize(),
                    "customization_script":
                    "python -m osdcquery.osdcquery %s '%s'" % (
                        data["query_name"], data["generated_query"]
                    )})])

            return HttpResponseRedirect(rest_url)

    return render(request, 'osdcquery/form.html', {
        'form': form,
        'query_fields': QueryFields()
    })

