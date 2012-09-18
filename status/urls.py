from django.conf.urls import patterns, include, url

urlpatterns = patterns('status.views',
    url(r'^$', 'status_public'),
)

