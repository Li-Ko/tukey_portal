from django.template.response import TemplateResponse
from django.shortcuts import render,redirect

from django.conf import settings

from .forms import RegisterIdForm
from openid_auth import pre_apply

def register_user(request, user=None, template_name='osdc/register.html'):
    if user is None:
        user = request.user

    form = RegisterIdForm()

    return render(request, template_name, {'form': form, 'method': user.method, 'identifier': user.lidentifier})

def slo(request):
    return redirect(settings.SINGLE_LOGOUT)

