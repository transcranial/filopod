from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import redirect
from django.http import HttpResponse
from main.models import *
import simplejson as json
from django.core.mail import send_mail
import traceback
import sys
from django.db import connection
from django.db.models import Q
import stripe
from main.views_exploration import get_user_generation
from main.views_exploration import get_user_Big_A
from django.core.cache import cache

'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
User Account view
requires user to be logged in
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
def profile(request):
    if request.user.is_authenticated():
		resources = Resource.objects.filter(user=request.user).only('datetime_added')
		try:
			plan = Plan.objects.get(user=request.user)
		except:
			plan = Plan.objects.get(id=4)
			plan.user.add(request.user)
			plan.save()
		plans = Plan.objects.all()
		all_plans = []
		for x in plans: 
			all_plans.append({'name':x.name,'price':x.price,'description':x.description})
		if len(resources) == 0:
			template_dict = {
				'resources_display': "None",
				'resource_num': 0,
				'subresource_num': 0,
				#'datetime_lastadded': "1900-01-01 00:00:00.000000",
				'datetime_lastadded': "",
				'resources_left': plan.resources,
				'resources_total': plan.resources,
				'plan_name': plan.name,
				'all_plans': all_plans,
				'message': "Sign up for a different plan:"
			}
			return render_to_response('tools/profile.html', template_dict, RequestContext(request))
		else:
			resource_num = resources.count()
			subresource_num = Subresource.objects.filter(containing_resource__user=request.user).count()
			datetime_lastadded = resources.latest('datetime_added').datetime_added
			template_dict = {
				'resource_num': resource_num,
				'subresource_num': subresource_num,
				'datetime_lastadded': datetime_lastadded,
				'resources_left': plan.resources - resource_num,
				'resources_total': plan.resources,
				'plan_name': plan.name,
				'all_plans': all_plans,
				'message': "Sign up for a different plan:"
			}
			return render_to_response('tools/profile.html', template_dict, RequestContext(request))
    else:
		return redirect('/accounts/login')
		
'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
User Billing view
requires user to be logged in
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
def bill(request):
    if request.user.is_authenticated():
		resources = Resource.objects.filter(user=request.user).only('datetime_added')
		old_plan = Plan.objects.get(user=request.user)
		new_plan = Plan.objects.get(name=request.POST['plan_selected'])
		plans = Plan.objects.all()
		all_plans = []
		for x in plans: 
			all_plans.append({'name':x.name,'price':x.price,'description':x.description})
		
		try:
			# Set your secret key: remember to change this to your live secret key in production
			# See your keys here https://manage.stripe.com/account
			stripe.api_key = "sk_test_aaTfLEH5D9uqFPTJcBqTNtie"

			# Get the credit card details submitted by the form
			token = request.POST['stripeToken']

			# Create a Customer
			customer = stripe.Customer.create(
			  card=token,
			  plan=new_plan.stripe_plan_id,
			  email=request.user.email
			)
			old_plan.user.remove(request.user)
			new_plan.user.add(request.user)
			success_charge = True
		except Exception:
			success_charge = False	
		
		if success_charge:
			if len(resources) == 0:
				template_dict = {
					'resources_display': "None",
					'resource_num': 0,
					'subresource_num': 0,
					#'datetime_lastadded': "1900-01-01 00:00:00.000000",
					'datetime_lastadded': "",
					'resources_left': new_plan.resources,
					'resources_total': new_plan.resources,
					'plan_name': new_plan.name,
					'all_plans': all_plans,
					'message': "Plan successfully updated to " + new_plan.name + ". Sign up for a different plan:"
				}
				return render_to_response('tools/profile.html', template_dict, RequestContext(request))
			else:
				resource_num = resources.count()
				subresource_num = Subresource.objects.filter(containing_resource__user=request.user).count()
				datetime_lastadded = resources.latest('datetime_added').datetime_added
				template_dict = {
					'resource_num': resource_num,
					'subresource_num': subresource_num,
					'datetime_lastadded': datetime_lastadded,
					'resources_left': new_plan.resources - resource_num,
					'resources_total': new_plan.resources,
					'plan_name': new_plan.name,
					'all_plans': all_plans,
					'message': "Plan successfully updated to " + new_plan.name + ". Sign up for a different plan:"
				}
				return render_to_response('tools/profile.html', template_dict, RequestContext(request))
		else:
			if len(resources) == 0:
				template_dict = {
					'resources_display': "None",
					'resource_num': 0,
					'subresource_num': 0,
					#'datetime_lastadded': "1900-01-01 00:00:00.000000",
					'datetime_lastadded': "",
					'resources_left': old_plan.resources,
					'resources_total': old_plan.resources,
					'plan_name': old_plan.name,
					'all_plans': all_plans,
					'message': "Credit card declined. Please contact us if problem persists. Try again:"
				}
				return render_to_response('tools/profile.html', template_dict, RequestContext(request))
			else:
				resource_num = resources.count()
				subresource_num = Subresource.objects.filter(containing_resource__user=request.user).count()
				datetime_lastadded = resources.latest('datetime_added').datetime_added
				template_dict = {
					'resource_num': resource_num,
					'subresource_num': subresource_num,
					'datetime_lastadded': datetime_lastadded,
					'resources_left': old_plan.resources - resource_num,
					'resources_total': old_plan.resources,
					'plan_name': old_plan.name,
					'all_plans': all_plans,
					'message': "Credit card declined. Please contact us if problem persists. Try again:"
				}
				return render_to_response('tools/profile.html', template_dict, RequestContext(request))
    else:
		return redirect('/accounts/login')

'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Resource Packages view
requires user to be logged in
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
def respacks(request):
    if request.user.is_authenticated():	
		template_dict = {}
		respack_avail = MatrixFiles.objects.filter(type='AtA').filter(~Q(user=request.user.id)).values_list('name',flat=True)
		respack_user = MatrixFiles.objects.filter(type='AtA').filter(user=request.user.id).values_list('name',flat=True)
		if len(respack_avail) == 0:
			template_dict.update({'respack_avail_list_display': ""})
		else:
			respack_avail_list_display = []	
			for respack in respack_avail:
				respack_avail_list_display.append('<li>' + respack + '</li>')
			template_dict.update({'respack_avail_list_display': respack_avail_list_display})
		if len(respack_user) == 0:
			template_dict.update({'respack_user_list_display': ""})
		else:
			respack_user_list_display = []	
			for respack in respack_user:
				respack_user_list_display.append('<li>' + respack + '</li>')
			template_dict.update({'respack_user_list_display': respack_user_list_display})
		return render_to_response('tools/respacks.html', template_dict, RequestContext(request))
    else:
		return redirect('/accounts/login')
		
'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Resource Packages: add resource package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
def respacks_user_add(request):
	if request.user.is_authenticated():
		user_ID = request.user.id
		try:
			respack_name = request.GET.get('respack_name', None)
			if respack_name:
				mf_old_ids = list(request.user.matrixfiles_set.values_list('id', flat=True))
				mf_new_ids = list(MatrixFiles.objects.filter(name=respack_name).values_list('id', flat=True))
				request.user.matrixfiles_set = list(set(mf_old_ids + mf_new_ids))
				res_old_ids = list(request.user.resource_set.values_list('id', flat=True))
				res_new_ids = list(Resource.objects.filter(type=respack_name).values_list('id', flat=True))
				request.user.resource_set = list(set(res_old_ids + res_new_ids))
				get_user_generation(user_ID)
				cache.incr('gen' + str(user_ID))
				get_user_Big_A.delay(user_ID, 1, 'freq')
				get_user_Big_A.delay(user_ID, 1, 'cov')
			return HttpResponse(status=200)
		except Exception as inst:
			print inst
			return HttpResponse(status=500)
	else:
		return redirect('/accounts/login')
		
'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Resource Packages: remove resource package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
def respacks_user_remove(request):
	if request.user.is_authenticated():
		user_ID = request.user.id
		try:
			respack_name = request.GET.get('respack_name', None)
			if respack_name:
				mf_old_ids = list(request.user.matrixfiles_set.values_list('id', flat=True))
				mf_remove_ids = list(MatrixFiles.objects.filter(name=respack_name).values_list('id', flat=True))
				request.user.matrixfiles_set = [x for x in mf_old_ids if x not in mf_remove_ids]
				res_old_ids = list(request.user.resource_set.values_list('id', flat=True))
				res_remove_ids = list(Resource.objects.filter(type=respack_name).values_list('id', flat=True))
				request.user.resource_set = [x for x in res_old_ids if x not in res_remove_ids]
				get_user_generation(user_ID)
				cache.incr('gen' + str(user_ID))
				get_user_Big_A.delay(user_ID, 1, 'freq')
				get_user_Big_A.delay(user_ID, 1, 'cov')
			return HttpResponse(status=200) 
		except Exception as inst:
			print inst
			return HttpResponse(status=500)
	else:
		return redirect('/accounts/login')

'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Resource Manager view
requires user to be logged in
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''		
def manage(request):
    if request.user.is_authenticated():
		resources_display = []		
		#domain_ID = 1 #default
		resources = Resource.objects.filter(user=request.user).only('id','type','identifier','journal','title','datetime_added')
		if len(resources) == 0:
			template_dict = {
				'resources_display': "None",
				'resource_num': 0,
				'subresource_num': 0,
				#'datetime_lastadded': "1900-01-01 00:00:00.000000"
				'datetime_lastadded': ""
			}
			return render_to_response('tools/manage.html', template_dict, RequestContext(request))
		else:
			for item in resources:
				if len(item.title) > 120:
					title_holder = item.title[0:120] + "..."
				else:
					title_holder = item.title
				resources_display.append('<li res_id="' + str(item.id) + '">(' + 
					item.type + ') [' + 
					item.identifier + '] <i>' + 
					item.journal + '</i><br>' + 
					title_holder + '.</li>')
			resource_num = resources.count()
			subresource_num = Subresource.objects.filter(containing_resource__user=request.user).count()
			datetime_lastadded = resources.latest('datetime_added').datetime_added
			template_dict = {
				'resources_display': resources_display,
				'resource_num': resource_num,
				'subresource_num': subresource_num,
				'datetime_lastadded': datetime_lastadded
			}
			return render_to_response('tools/manage.html', template_dict, RequestContext(request))
    else:
		return redirect('/accounts/login')

'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Subresource viewer
requires user to be logged in
-called when details button pushed in Resource Manager page
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''	
def manage_viewsubres(request):
    if request.user.is_authenticated():
		try:
			res_id = request.GET.get('res_id','')	
			subresources_display = []		
			subresources = Subresource.objects.filter(containing_resource__user=request.user).filter(containing_resource__id=res_id)
			resource = Resource.objects.get(id=res_id)
			resource_display = '(' + resource.type + ') [' + resource.identifier + '] <i>' + resource.journal + '</i><br>' + resource.title + '.    <a href="' + resource.url + '" style="text-decoration:none" target="_blank">[link]</a><br>' + resource.author
			for item in subresources:
				if item.content:
					content = item.content
				else:
					content = ''
				if item.url:
					url = item.url
				else:
					url = ''
				subresources_display.append('<li content="' + content +'" url="' + url +'">(' + 
					item.type + ') [' + 
					item.name + ']<br>' + 
					content[:35] + '...</li>')
			template_dict = {
				'resource_display': resource_display,
				'subresources_display': subresources_display
			}
			return render_to_response('tools/manage_viewsubres.html', template_dict, RequestContext(request))
		except Exception as inst:
			print inst
			return HttpResponse(status=500)
    else:
		return redirect('/accounts/login')

'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Apps installation view
does not require user to be logged in
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''		
def install(request):
	page = request.GET.get('page','')	
	return render_to_response('install/' + page + '.html', RequestContext(request))

'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Help view
does not require user to be logged in
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''		
def help(request):
	page = request.GET.get('page','')	
	return render_to_response('help/' + page + '.html', RequestContext(request))

'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
About view
does not require user to be logged in
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''		
def about(request):
	page = request.GET.get('page','')	
	return render_to_response('about/' + page + '.html', RequestContext(request))

'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Contact Us - Feedback
Sends email to feedback account based on form user fills out
requires user to be logged in
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''		
def contact_feedback(request):
    if request.user.is_authenticated():
		user_name = request.POST.get('username', None)
		user_email = request.POST.get('email', None)
		f_name = request.POST.get('f_name', None)
		f_email = request.POST.get('f_email', None)
		f_message = request.POST.get('f_message', None)
		msgbody = 'registered username: ' + user_name + '\n'
		msgbody = msgbody + 'registered email: ' + user_email + '\n\n'
		msgbody = msgbody + 'name on form: ' + f_name + '\n'
		msgbody = msgbody + 'email on form: ' + f_email + '\n\n'
		msgbody = msgbody + 'MESSAGE:\n\n' + f_message
		try:
			send_mail('Filopod feedback', msgbody, 'admin@filopod.com', ['admin@filopod.com'])
			return HttpResponse(status=200)
		except Exception as inst:
			print inst
			traceback.print_exc()
			return HttpResponse(status=500)
    else:
		return redirect('/accounts/login')
	
'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Contact Us - Support
Sends email to support account based on form user fills out
requires user to be logged in
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''		
def contact_support(request):
    if request.user.is_authenticated():
		user_name = request.POST.get('username', None)
		user_email = request.POST.get('email', None)
		f_name = request.POST.get('f_name', None)
		f_email = request.POST.get('f_email', None)
		f_message = request.POST.get('f_message', None)
		msgbody = 'registered username: ' + user_name + '\n'
		msgbody = msgbody + 'registered email: ' + user_email + '\n\n'
		msgbody = msgbody + 'name on form: ' + f_name + '\n'
		msgbody = msgbody + 'email on form: ' + f_email + '\n\n'
		msgbody = msgbody + 'MESSAGE:\n\n' + f_message		
		try:
			send_mail('Filopod support request - username ' + user_name, msgbody, 'admin@filopod.com', ['accounts@filopod.com'])
			return HttpResponse(status=200)
		except Exception as inst:
			print inst
			traceback.print_exc()
			return HttpResponse(status=500)
    else:
		return redirect('/accounts/login')

'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
About - More Resources - Request a Journal
Sends email to admin account based on journal request
requires user to be logged in
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''		
def requestjournal(request):
    if request.user.is_authenticated():
		print "this worked."
		user_name = request.POST.get('username', None)
		user_email = request.POST.get('email', None)
		journal_name = request.POST.get('journal_name', None)
		msgbody = 'registered username: ' + user_name + '\n'
		msgbody = msgbody + 'registered email: ' + user_email + '\n\n'
		msgbody = msgbody + 'Journal Suggestion:\n\n' + journal_name		
		try:
			send_mail('Filopod journal suggestion from ' + user_name, msgbody, 'admin@filopod.com', ['alvinyu@post.harvard.edu'])
			return HttpResponse(status=200)
		except Exception as inst:
			print inst
			traceback.print_exc()
			return HttpResponse(status=500)
    else:
		return redirect('/accounts/login')