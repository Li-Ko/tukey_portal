from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from datasets.models import DataSet, Key, KeyValue
from datetime import datetime

#This needs work -- a lot of assumptions about the key/values

initial_key = 1000
time_format = "%Y-%m-%dT%H:%M:%S"

def get_next_ark_key(prefix):
    dataset_list = DataSet.objects.all().order_by('-num')
    if len(dataset_list) < 0:
        return prefix + str(initial_key)

    #might want to cache last_key in the future -- won't have to do the db query
    last_key = dataset_list[0].num
    return prefix + str(last_key + 1)

def add_key_value(ark_key_str, key_name_str, value_str):
    d = DataSet.objects.get(ark_key=ark_key_str)
    k = Key.objects.get(key_name=key_name_str)

    #should some validation be done?
    key_value = KeyValue(dataset=d, key=k, value=value_str)
    key_value.save()


def datasets_list_index(request, category_filter=None):
    titles = dict()
    short_descripts = dict()
    categories = dict()
    modified_times = dict()

    datasets = []

    #this is terrible, executing a query for each key/value, needs to be fixed
    if category_filter is not None:
        kvs = KeyValue.objects.filter(key='category', value=category_filter)
        for kv in kvs:
            datasets.append(kv.dataset)
            titles[kv.dataset.ark_key] = KeyValue.objects.get(dataset=kv.dataset, key='title').value
            short_descripts[kv.dataset.ark_key] = KeyValue.objects.get(dataset=kv.dataset, key='short_description').value
            for category in KeyValue.objects.filter(dataset=kv.dataset, key='category'):
                if kv.dataset.ark_key not in categories:
                    categories[kv.dataset.ark_key] = []
                categories[kv.dataset.ark_key].append(category.value)
            modified_times[kv.dataset.ark_key] = datetime.strptime(KeyValue.objects.get(dataset=kv.dataset, key='modified').value, time_format)

    else:
        datasets = DataSet.objects.all()

        #better way to do this? -- assuming one value for everything except categories
        for title in KeyValue.objects.filter(key='title'):
            titles[title.dataset.ark_key] = title.value

        for descript in KeyValue.objects.filter(key='short_description'):
            short_descripts[descript.dataset.ark_key] = descript.value

        for category in KeyValue.objects.filter(key='category'):
            if category.dataset.ark_key not in categories:
                categories[category.dataset.ark_key] = []
            categories[category.dataset.ark_key].append(category.value)
    
        for time in KeyValue.objects.filter(key='modified'):
            modified_times[time.dataset.ark_key] = datetime.strptime(time.value, time_format)
    
    return render_to_response('datasets/datasets_list_index.html', {'datasets' : datasets, 'titles' : titles, 'categories' : categories, 'short_descripts' : short_descripts, 'modified_times' : modified_times, 'category_filter' : category_filter}, context_instance=RequestContext(request))

def dataset_detail(request, dataset_id):
    d = get_object_or_404(DataSet, pk=dataset_id)
    dataset_dict = dict()
    dataset_dict['title'] = KeyValue.objects.get(dataset=d, key='title').value
    dataset_dict['source'] = KeyValue.objects.get(dataset=d, key='source').value
    dataset_dict['source_url'] = KeyValue.objects.get(dataset=d, key='source_url').value
    dataset_dict['description'] = KeyValue.objects.get(dataset=d, key='description').value
    categories = KeyValue.objects.filter(dataset=d, key='category').order_by('value')
    dataset_dict['categories'] = []
    for category in categories:
    	dataset_dict['categories'].append(category.value)
    dataset_dict['size'] = KeyValue.objects.get(dataset=d, key='size').value
    dataset_dict['osdc_location'] = KeyValue.objects.get(dataset=d, key='osdc_location').value
    dataset_dict['osdc_folder'] = KeyValue.objects.get(dataset=d, key='osdc_folder').value
    dataset_dict['osdc_hs_location'] = KeyValue.objects.get(dataset=d, key='osdc_hs_location').value
    dataset_dict['osdc_hs_folder'] = KeyValue.objects.get(dataset=d, key='osdc_hs_folder').value

    return render_to_response('datasets/dataset_detail.html', {'dataset': dataset_dict}, context_instance=RequestContext(request))
