from django.template.response import TemplateResponse
from django.shortcuts import render


from .forms import RegisterIdForm
from openid_auth import pre_apply

def register_user(request, user=None, template_name='osdc/register.html'):
    return pre_apply(request)

