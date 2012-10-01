# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 Nebula, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
URL patterns for the OpenStack Dashboard.
"""

from django.conf.urls.defaults import patterns, url, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.simple import direct_to_template
import horizon

from tukey.shibboleth_auth import patch_openstack_middleware_get_user

patch_openstack_middleware_get_user()

urlpatterns = patterns('',
    url(r'^$', direct_to_template, {"template": "index.html"}, name="index"),
    url(r'^console/', 'horizon.views.splash', name='splash'),
    url(r'^openid/', include('django_openid_auth.urls', namespace='openid')),
    url(r'^auth/', include('openstack_auth.urls')),
    url(r'^files/', include('files.urls', namespace='files')),
    url(r'^tukey_admin/', include('tukey_admin.urls', namespace='tukey_admin')),
    url(r'^status/', include('status.urls', namespace='status')),
    url(r'^sponsors/', direct_to_template, {"template": "sponsors.html"}, name="sponsors"),                   
    url(r'^news/', direct_to_template, {"template": "news.html"}, name="news"),
    url(r'^projects/', direct_to_template, {"template": "projects.html"}, name="projects"),
    url(r'', include('webforms.urls')),                   
    url(r'', include(horizon.urls)))

# Development static app and project media serving using the staticfiles app.
urlpatterns += staticfiles_urlpatterns()

# Convenience function for serving user-uploaded media during
# development. Only active if DEBUG==True and the URL prefix is a local
# path. Production media should NOT be served by Django.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
