from django.conf import settings
from django.forms.util import ErrorList
from django.http import HttpResponseRedirect
from django.shortcuts import render
from tukey.webforms.forms import OSDCForm, OSDCSupportForm
import smtplib

def build_message(form):
    msg_list = []
    msg_list.append('From:\n')
    msg_list.append(form.cleaned_data['name'])
    msg_list.append('\n')
    msg_list.append(form.cleaned_data['email'])
    msg_list.append('\n\nOrganization/University\n')
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

    msg_list.append('\n\nAccess Requested:\n')
    for item in form.cleaned_data['systems']:
        if item == 'OSDC-Sullivan':
            msg_list.append('OSDC-Sullivan\n')
        elif item == 'OSDC-Adler':
            msg_list.append('OSDC-Adler\n')
        elif item == 'OSDC-Atwood':
            msg_list.append('OSDC-Atwood\n')
        elif item == 'occ-y':
            msg_list.append('OCC-Y\n')
        elif item == 'bionimbus_cc':
            msg_list.append('Bionimbus Community Cloud\n')
        elif item == 'bionimbus_uchicago':
            msg_list.append('UChicago Bionimbus Cloud\n')
        elif item == 'matsu':
            msg_list.append('Matsu Testbed\n')

    msg_list.append('\n\nProject Name:\n')
    msg_list.append(form.cleaned_data['projectname'])
    msg_list.append('\n\nProject Description\n')
    msg_list.append(form.cleaned_data['projectdescr'])
    msg_list.append('\n\nProject Lead\n')
    msg_list.append(form.cleaned_data['projectlead'])
    msg_list.append('\n\nProject Lead E-mail:\n')
    msg_list.append(form.cleaned_data['projectlead_email'])
    msg_list.append('\n\nEstimated Resources:\n')
    msg_list.append(form.cleaned_data['resources'])
    return ''.join(msg_list)

def osdc_apply(request):
    if request.method == 'POST': # If the form has been submitted...
        form = OSDCForm(request.POST, request.FILES) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            subject = 'OSDC Account Request'
            message = build_message(form)
            sender = form.cleaned_data['email']

            recipients = [settings.APPLICATION_EMAIL]

            from django.core.mail import EmailMessage
            email = EmailMessage(subject, message, sender, recipients)

            if "pubkey" in request.FILES:
                pubkey = request.FILES["pubkey"]
                email.attach(pubkey.name, pubkey.read(), pubkey.content_type)

            try:
                email.send()
                return HttpResponseRedirect('thanks/') # Redirect after POST

            except smtplib.SMTPRecipientsRefused as e:
                form._errors["email"] = ErrorList(
                    [u"Domain of address %s does not exist" % sender])

    else:
        form = OSDCForm() # An unbound form

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
