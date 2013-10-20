from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('tukey.vm.views',
    #url(r'^(?P<ip>.+)/(?P<port>\d+)/(?P<path>\w*)$', 'reverse_proxy'),
    url(r'^(?P<ip>.+)/(?P<path>\w*)$', 'reverse_proxy'),
)

