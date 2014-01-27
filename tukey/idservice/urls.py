from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('tukey.idservice.views',
    url(r'^$', 'index'),
)
