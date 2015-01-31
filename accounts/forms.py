from django import forms
from registration_email.forms import EmailRegistrationForm
from django.utils.translation import ugettext_lazy as _

attrs_dict = {'class': 'required'}

class CustomEmailRegistrationForm(EmailRegistrationForm):
	first_name = forms.CharField(label=_(u'First Name'), error_messages={'required': _("Please enter your first name")})
	last_name = forms.CharField(label=_(u'Last Name'), error_messages={'required': _("Please enter your last name")})
	tos = forms.BooleanField(widget=forms.CheckboxInput(attrs=attrs_dict), label=_(u'I have read and agree to the Terms of Service'), error_messages={'required': _("You must agree to the terms to register")})