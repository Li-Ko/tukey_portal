from django import forms
from captcha.fields import ReCaptchaField

class MyCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        html = super(MyCheckboxSelectMultiple, self).render(name, value, attrs, choices)
        return mark_safe(html.replace('<ul>', '<ul class="foobar">'))

SYSTEM_CHOICES = (
    ('OSDC-Sullivan', 'OSDC-Sullivan (newest OpenStack based cloud)'),
    ('OSDC-Adler', 'OSDC-Adler (Eucalyptus based cloud)'),
    ('OSDC-Atwood', 'OSDC-Atwood (A protected data cloud, home of the Conte Center Cloud)'),
    #('bionimbus_web', 'Bionimbus Web Portal'),
    ('OSDC-Skidmore', 'OSDC-Skidmore (newest Hadoop cluster)'),
    ('occ-y', 'OCC-Y (Hadoop cluster donated by Yahoo!)'),
    ('matsu', 'Matsu Hadoop Testbed'),
    ('bionimbus_uchicago', 'UChicago Bionimbus Cloud (private cloud for genomics projects at UChicago)'),
    )

class OSDCForm(forms.Form):
    name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class' : 'span4'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'class' : 'span4'}))
    login_email = forms.EmailField(widget=forms.TextInput(attrs={'class' : 'span4'}), required=False)
    organization = forms.CharField(max_length=200,widget=forms.TextInput(attrs={'class' : 'span4'}))

    systems = forms.MultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple, choices=SYSTEM_CHOICES,
        initial=["OSDC-Sullivan"])

    webpage = forms.CharField(max_length=200,required=False,widget=forms.TextInput(attrs={'class' : 'span4'}))
    phonenumber = forms.CharField(max_length=100,required=False,widget=forms.TextInput(attrs={'class' : 'span4'}))
    address = forms.CharField(required=False,widget=forms.Textarea(attrs={'class' : 'span4', 'rows' : '4'}))
    projectname = forms.CharField(widget=forms.TextInput(attrs={'class' : 'span4'}))
    projectlead = forms.CharField(max_length=200,widget=forms.TextInput(attrs={'class' : 'span4'}))
    projectlead_email = forms.EmailField(widget=forms.TextInput(attrs={'class' : 'span4'}))
    projectdescr = forms.CharField(widget=forms.Textarea(attrs={'class' : 'span5'}))
    #othercontacts = forms.CharField(required=False)
    resources = forms.CharField(widget=forms.Textarea(attrs={'class' : 'span5'}))
    pubkey = forms.FileField(widget=forms.ClearableFileInput(attrs={'class' : 'span4'}), required=False)
    captcha = ReCaptchaField()

class OSDCSupportForm(forms.Form):
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea(attrs={'class' : 'span5'}))
    sender = forms.EmailField()
    #captcha = ReCaptchaField()

