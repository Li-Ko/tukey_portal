from django.conf.urls import patterns, include, url

urlpatterns = patterns('datasets.views',
    url(r'^$', 'datasets_list_index', name='datasets_list_index'),
    url(r'^(?P<dataset_id>\w+)/$', 'dataset_detail', name='dataset_detail'), 
    url('^category/(?P<category_filter>.*)/$', 'datasets_list_index', name='datasets_category'),                
)
