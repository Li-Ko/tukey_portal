#  Copyright 2014 Open Cloud Consortium
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at #
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
''' views for single sign on '''

from django.shortcuts import render

from .forms import RegisterIdForm

def register_user(request, user=None, template_name='osdc/register.html'):
    ''' Registration '''
    if user is None:
        user = request.user

    form = RegisterIdForm()

    return render(request, template_name, {'form': form, 'method': user.method,
            'identifier': user.lidentifier})
