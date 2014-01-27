# Create your views here.
from django.conf import settings
from django.shortcuts import render, render_to_response
from django import forms
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from tukey_middleware.modules.ids import client
from tukey.osdcquery.forms import OsdcQueryForm, QueryFields
import json
import pyelasticsearch

@login_required
def index(request):
    addr = settings.ID_SERVICE_URL
    token = request.user.token.id
    username = request.user.username
    tenant = request.user.tenant_name

    service_client = client.Client(id_service = addr,
                                   os_username = username,
                                   os_tenant_name = tenant,
                                   os_auth_token = token)

    projects = service_client.get_projects(write=True)
    choices = []
    for project in projects:
        choices.append((project['id'], project['name']))

    class UploadForm(forms.Form):
        generated_json = forms.CharField(
            required=False,
            label="Generated JSON",
            widget=forms.HiddenInput(attrs={'class':'span9','id': 'generated_json'}))
        project = forms.ChoiceField(label="Project", choices=choices)
        file = forms.FileField(label="File", required=False)

    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            my_file = None
            if 'file' in request.FILES:
                my_file = request.FILES['file']
            project = form.cleaned_data['project']
            my_json = form.cleaned_data['generated_json']
            if my_file:
                data = my_file.read()
                name = my_file.name
            elif len(my_json) > 2:
                D = json.loads(my_json)
                my_files = D.pop('filename')
                if isinstance(my_files, list):
                    temp = []
                    for f in my_files:
                        temp.append({'filesize':0,'filename':f})
                    D['files'] = {'file': temp}
                else:
                    D['files'] = {'file': [{'filesize':0, 'filename':my_files}]}
                data = D
                name = data
            else:
                return render(request, 'idservice/error.html', {'data': name, 'project': project})
            result = service_client.upload_metadata(project, [data])[0]
            return render(request, 'idservice/thanks.html', {'id': result, 'data': name, 'project': project})
    else:
        form = UploadForm()
    (query_fields, choices_dict) = form_helper()
    return render(request, 'idservice/idservice.html', {
        'form': form,
        'query_fields': query_fields,
        'choices_dict': choices_dict
    })



def form_helper():
    query_url = 'http://172.16.1.160:9200'
    query_index = 'tcga-cghub'
    query_doc_type = 'analysis'
    es = pyelasticsearch.ElasticSearch(query_url)
    facet_query = {
        "fields": ["_id", "analysis_id", "center_name", "files", "upload_date"],
        "query" : {
            "matchAll" : {}
            },
        "facets" : {
            "center_name" : { "terms" : {"field" : "center_name", "size": 50}},
            "platform" : {"terms" : {"field" : "platform", "size": 50}},
            "sample_id" : { "terms" : {"field" : "sample_id", "size": 50}},
            "disease_abbr" : {"terms" : {"field" : "disease_abbr", "size":50}},
            "participant_id" : {"terms" : {"field" : "participant_id", "size":50}},
            "analyte_code" : {"terms" : {"field" : "analyte_code", "size": 50}},
            "sample_type" : {"terms" : {"field" : "sample_type", "size": 50}},
            "tss_id" : {"terms" : {"field" : "tss_id", "size": 50}},
            "analysis_id" : {"terms" : {"field" : "analysis_id", "size": 50}},
            "state" : {"terms" : {"field" : "state", "size": 50}},
            "study" : {"terms" : {"field" : "study", "size": 50}},
            "aliquot_id" : {"terms" : {"field" : "aliquot_id", "size": 50}},
            "sample_accession" : {"terms" : {"field" : "sample_accession", "size": 50}},
            "last_modified" : {"terms" : {"field" : "last_modified", "size": 50}},
            "library_strategy" : {"terms" : {"field" : "library_strategy", "size": 50}},
            "filename" : {"terms" : {"field" : "filename", "size": 50}}

            }
        }

    facets = es.search(facet_query, index=query_index, doc_type=query_doc_type)

    choices_dict = {}
    choices_list = []

    for k,v in facets["facets"].items():
        other = v["other"]
        if other == 0:
            choices_dict[k] = []

            for item in v["terms"]:
                choices_dict[k].append(item["term"])

    for k,v in facets["facets"].items():
        other = v["other"]
        if other == 0:
            choices_list.append((k, [item["term"] for item in v["terms"]]))

    sorted_choices_dict = {}
    for k, v in choices_dict.items():
        sorted_choices_dict[k] = sorted(v)

    sorted_choices_list = sorted(choices_list, key=lambda tup: tup[0])
    sorted_choices_dict = {}
    for k,v in choices_dict.items():
        sorted_choices_dict[k] = sorted(v)

    qf = QueryFields()
    for field in qf:
        print qf

    return (qf, sorted_choices_dict)
