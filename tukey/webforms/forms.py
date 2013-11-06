from django import forms
from captcha.fields import ReCaptchaField

class MyCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        html = super(MyCheckboxSelectMultiple, self).render(name, value, attrs, choices)
        return mark_safe(html.replace('<ul>', '<ul class="foobar">'))

SYSTEM_CHOICES = (
    ('OSDC-Sullivan', 'OSDC-Sullivan (newest OpenStack based cloud)'),
   # ('OSDC-Adler', 'OSDC-Adler (Eucalyptus based cloud)'),
   # ('OSDC-Atwood', 'OSDC-Atwood (A protected data cloud, home of the Conte Center Cloud)'),
   # ('bionimbus_web', 'Bionimbus Web Portal'),
   # ('OSDC-Skidmore', 'OSDC-Skidmore (newest Hadoop cluster)'),
    ('occ-y', 'OCC-Y (Hadoop cluster donated by Yahoo!)'),
   # ('matsu', 'Matsu Hadoop Testbed'),
   # ('bionimbus_uchicago', 'UChicago Bionimbus Cloud (private cloud for genomics projects at UChicago)'),
    )

CPU_CHOICES = (
	('lte16', '16 cores or less'),
	('16plus', 'More than 16 cores'),
)

STORAGE_CHOICES = (
	('lte1', '1 terabyte or less'),
	('1plus', 'More than 1 terabyte'),
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
    sharing = forms.CharField(widget=forms.TextInput(attrs={'class' : 'span4'}), required=False)
    # othercontacts = forms.CharField(required=False)
    # Below line commented out because split into "cpus" and "storage" as follows.
    # resources = forms.CharField(widget=forms.Textarea(attrs={'class' : 'span5'}))
    cpus = forms.ChoiceField(widget=forms.Select(attrs={'class' : 'span4'}), choices=CPU_CHOICES)
    more_cpus = forms.CharField(widget=forms.TextInput(attrs={'id' : 'more_cpus', 'class' : 'span4'}), required=False)
    storage = forms.ChoiceField(widget=forms.Select(attrs={'class' : 'span4'}), choices=STORAGE_CHOICES)
    more_storage = forms.CharField(widget=forms.TextInput(attrs={'id' : 'more_storage', 'class' : 'span4'}), required=False)
    pubkey = forms.FileField(widget=forms.ClearableFileInput(attrs={'class' : 'span4'}), required=False)
    referral_source = forms.CharField(widget=forms.TextInput(attrs={'class' : 'span4'}))
    # captcha = ReCaptchaField()

    # TODO: Conditional validation for more_cpus and more_storage fields
    # def clean(self):
	# cleaned_data = super(OSDCForm, self).clean()
	# more code here...


class OSDCSupportForm(forms.Form):
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea(attrs={'class' : 'span5'}))
    sender = forms.EmailField()
    #captcha = ReCaptchaField()

class OSDCDemoForm(forms.Form):
    first_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class' : 'span4'}))
    last_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class' : 'span4'}))
    organization = forms.CharField(max_length=200,widget=forms.TextInput(attrs={'class' : 'span4'}))
    projectlead = forms.CharField(max_length=200,widget=forms.TextInput(attrs={'class' : 'span4'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'class' : 'span4'}))
    how = forms.CharField(widget=forms.Textarea(attrs={'class' : 'span5'}))

