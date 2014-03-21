import smtplib

from django.conf import settings
from django.contrib.auth import logout
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.core.mail import send_mail, BadHeaderError
from django.core.validators import validate_email
from django.forms.util import ErrorList
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django_openid_auth.views import parse_openid_response
from openid.consumer.consumer import SUCCESS
from tukey.openid_auth import pre_apply
from tukey.webforms.forms import OSDCForm, OSDCSupportForm, OSDCDemoForm

def build_message(form):
    msg_list = []
    msg_list.append('Summary of submitted information:\n\n')
    msg_list.append('From:\n')
    msg_list.append(form.cleaned_data['first_name'])
    msg_list.append(' ')
    msg_list.append(form.cleaned_data['last_name'])
    msg_list.append('\n')
    msg_list.append(form.cleaned_data['email'])
    msg_list.append('\neRA Commons Username:\n')
    msg_list.append(form.cleaned_data['eracommons'])
    msg_list.append('\nidentifier:\n')
    msg_list.append(form.cleaned_data['eppn'])
    msg_list.append('\nOrganization/University:\n')
    msg_list.append(form.cleaned_data['organization'])

    if form.cleaned_data['webpage'] != '':
        msg_list.append('\n\nWeb page:\n')
        msg_list.append(form.cleaned_data['webpage'])
    if form.cleaned_data['phonenumber'] != '':
        msg_list.append('\n\nPhone number:\n')
        msg_list.append(form.cleaned_data['phonenumber'])
    if form.cleaned_data['address'] != '':
        msg_list.append('\n\nAddress:\n')
        msg_list.append(form.cleaned_data['address'])

    msg_list.append('\n\nProject Name:\n')
    msg_list.append(form.cleaned_data['projectname'])
    msg_list.append('\n\nProject Description\n')
    msg_list.append(form.cleaned_data['projectdescr'])

    if (form.cleaned_data['sharing'] != ""):
        msg_list.append('\n\nSharing with:\n')
        msg_list.append(form.cleaned_data['sharing'])

    msg_list.append('\n\nProject Lead\n')
    msg_list.append(form.cleaned_data['projectlead'])
    msg_list.append('\n\nProject Lead E-mail:\n')
    msg_list.append(form.cleaned_data['projectlead_email'])
    msg_list.append('\n\nEstimated CPUs:\n')
    msg_list.append(form.cleaned_data['cpus'])

    if form.cleaned_data['more_cpus'] != "":
        msg_list.append("(Specific requirements: " + form.cleaned_data['more_cpus'] + ")")

    msg_list.append('\n\nEstimated storage:\n')
    msg_list.append(form.cleaned_data['storage'])

    if form.cleaned_data['more_storage'] != "":
        msg_list.append("(Specific requirements: " + form.cleaned_data['more_storage'] + ")")

    msg_list.append('\n\nHeard about PDC from:\n')
    msg_list.append(form.cleaned_data['referral_source'])
    msg_list.append('\n\n')
    return ''.join(msg_list)

def osdc_apply(request, user=None):
    if user is None:
        user = request.user

    if request.method == 'POST': # If the form has been submitted...
        form = OSDCForm(request.POST, request.FILES) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            subject = 'Bionimbus PDC Account Request'
            message_admin = build_message(form)
            sender_admin = form.cleaned_data['email']
            recipients_admin = [settings.APPLICATION_EMAIL]

            # Values for confirmation email to user ('Subject' remains same)
            message_user = "Thank you for your application to the Bionimbus PDC. "
            message_user += "Someone from our team will contact you within one business day.\n\n%s" % message_admin
            sender_user = 'noreply@opensciencedatacloud.org'
            recipients_user = [sender_admin]

            email_admin = EmailMessage(subject, message_admin, sender_admin, recipients_admin)
            email_user = EmailMessage(subject, message_user, sender_user, recipients_user)

            if "pubkey" in request.FILES:
                pubkey = request.FILES["pubkey"]
                email_admin.attach(pubkey.name, pubkey.read(), pubkey.content_type)
                email_user.attach(pubkey.name, pubkey.read(), pubkey.content_type)

            try:
                email_admin.send()
                email_user.send()
                if not request.user.is_authenticated():
                    logout(request)
                    # Redirect after POST
                return HttpResponseRedirect('thanks/')

            except smtplib.SMTPRecipientsRefused as e:
                form._errors["email"] = ErrorList(
                    # Changed 'sender' to 'sender_admin' after code split into two emails.
                    [u"Domain of address %s does not exist" % sender_admin])

    else:
        if request.user.is_authenticated():
            form = OSDCForm(initial={"eracommons": user.username,
                    "eppn": user.username,
                    "method": "re-apply"})
        elif hasattr(user, 'identifier'):
            form = OSDCForm(initial={"eppn": user.identifier,
                    "eracommons": user.identifier.split("!")[-1],
                    "method": user.method})
        else:
            return HttpResponseRedirect('/pre_apply/?next=/apply/')

    return render(request, 'webforms/osdc_apply.html', {
        'form': form,
    })

def osdc_apply_thanks(request):
    return render(request, 'webforms/apply_thanks.html')

def support(request):
    if request.method == 'POST': # If the form has been submitted...
        form = OSDCSupportForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            sender = form.cleaned_data['sender']

            recipients = [settings.SUPPORT_EMAIL]

            from django.core.mail import send_mail
            send_mail(subject, message, sender, recipients)
            return HttpResponseRedirect('thanks/') # Redirect after POST

    else:
        form = OSDCSupportForm() # An unbound form

    return render(request, 'webforms/support_form.html', {
        'form': form,
    })

def support_thanks(request):
    return render(request, 'webforms/support_thanks.html')

def osdc_demo(request):
    if request.method == 'POST': # If the form has been submitted...
        form = OSDCDemoForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            subject = "Demo Registration"# form.cleaned_data['subject']
            message = ""
            for k, v in form.cleaned_data.items():
                message += k + ": " + v + "\n"
            #message = str(form.cleaned_data)
            sender = form.cleaned_data['email']

            recipients = [settings.DEMO_REG_EMAIL]

            from django.core.mail import send_mail
            send_mail(subject, message, sender, recipients)
            return HttpResponseRedirect('thanks/') # Redirect after POST

    else:
        form = OSDCDemoForm() # An unbound form

    return render(request, 'webforms/demo_form.html', {
        'form': form,
    })


def osdc_demo_thanks(request):
    return render(request, 'webforms/demo_thanks.html', {
        'email': settings.DEMO_REG_EMAIL
    })
