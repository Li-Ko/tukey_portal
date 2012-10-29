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

import re

from django import shortcuts
from django.core import validators
from django.utils.translation import ugettext_lazy as _

from horizon import api
from horizon import exceptions
from horizon import forms
from horizon import messages

from tukey.cloud_attribute import cloud_names, cloud_details, has_function


NEW_LINES = re.compile(r"\r|\n")


# mgreenway hacking the view to provide cloud where needed

#to generate a keypair for the login-nodes
KEYPAIR_LOGIN_CHOICES = {'all': 'Use this keypair with all resources.'}

LOGIN_NODES = {'login' + name: name.title() + ' login node.'
    for name in cloud_names()}

KEYPAIR_LOGIN_CHOICES.update(LOGIN_NODES)


CREATE_KEYPAIR_CLOUD_CHOICES=((key, _(value)) for (key, value) in dict(
    cloud_details(), **KEYPAIR_LOGIN_CHOICES).items() 
	    if has_function('create_keypair', key))

IMPORT_KEYPAIR_CLOUD_CHOICES=((key, _(value)) for (key, value) in dict(
    cloud_details(), **KEYPAIR_LOGIN_CHOICES).items()
            if has_function('import_keypair', key))

CREATE_KEYPAIR_CLOUD = forms.ChoiceField(label=_("Resource"),required=True,
                                choices=CREATE_KEYPAIR_CLOUD_CHOICES)

IMPORT_KEYPAIR_CLOUD = forms.ChoiceField(label=_("Resource"),required=True,
                                choices=IMPORT_KEYPAIR_CLOUD_CHOICES)



class CreateKeypair(forms.SelfHandlingForm):
    name = forms.CharField(max_length="20",
                           label=_("Keypair Name"),
                           validators=[validators.validate_slug],
                           error_messages={'invalid': _('Keypair names may '
                                'only contain letters, numbers, underscores '
                                'and hyphens.')})

    cloud = CREATE_KEYPAIR_CLOUD

    def handle(self, request, data):
        return True  # We just redirect to the download view.


class ImportKeypair(forms.SelfHandlingForm):
    name = forms.CharField(max_length="20", label=_("Keypair Name"),
                 validators=[validators.RegexValidator('\w+')])
    public_key = forms.CharField(label=_("Public Key"), widget=forms.Textarea)

    cloud = IMPORT_KEYPAIR_CLOUD

    def handle(self, request, data):
        try:
            # Remove any new lines in the public key
            data['public_key'] = NEW_LINES.sub("", data['public_key'])
            keypair = api.keypair_import(request,
                                         data['cloud'] + '-' + data['name'],
                                         data['public_key'])
            messages.success(request, _('Successfully imported public key: %s')
                                       % data['name'])
            return keypair
        except:
            exceptions.handle(request, ignore=True)
            self.api_error(_('Unable to import keypair.'))
            return False
