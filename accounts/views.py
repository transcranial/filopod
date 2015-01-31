from django.contrib.auth.views import login
from django.shortcuts import render_to_response
from django.template import RequestContext
from registration_email.forms import EmailAuthenticationForm
		
def login_mod(request):
	if request.POST.get('PersistentCookie') is None:
		request.session.set_expiry(0)
	else:
		request.session.set_expiry(None)		
	return login(request, template_name='registration/login.html',
          authentication_form=EmailAuthenticationForm,
          current_app=None, extra_context=None)