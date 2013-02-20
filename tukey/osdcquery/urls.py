from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.query_builder, name='query_builder'),
    url(r'^select_field/', views.select_field, name='select_field'),
#    url(r'^query/$', views.query, name='query'),
)
