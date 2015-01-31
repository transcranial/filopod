from django.conf.urls import patterns, include, url
from accounts.forms import CustomEmailRegistrationForm

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'filopod.views.home', name='home'),
    # url(r'^filopod/', include('filopod.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    
    url(r'^$', 'filopod.views.home', name='home'),
    url(r'^accounts/login/$', 'accounts.views.login_mod', name='login_mod'),
    url(r'^accounts/register/$', 'registration.views.register', {'backend': 'registration.backends.default.DefaultBackend',
        'form_class': CustomEmailRegistrationForm}, name='registration_register'),
    url(r'^accounts/', include('registration_email.backends.default.urls')),
    url(r'^get_search_concepts', 'filopod.views.get_search_concepts', name='get_search_concepts'),
    url(r'^get_concept_nodes', 'filopod.views.get_concept_nodes', name='get_concept_nodes'),
    url(r'^fetch_resources', 'filopod.views.fetch_resources', name='fetch_resources'),
    url(r'^about', 'filopod.views.about', name='about'),
    url(r'^doc/tos/$', 'filopod.views.tos', name='tos'),
    url(r'^doc/privacy/$', 'filopod.views.privacy', name='privacy'),
    url(r'^doc/publishers/$', 'filopod.views.publishers', name='publishers'),
    
    # includes:
    # ^accounts/ ^login/$ [name='auth_login']
    # ^accounts/ ^logout/$ [name='auth_logout']
    # ^accounts/ ^activate/complete/$ [name='registration_activation_complete']
    # ^accounts/ ^activate/(?P<activation_key>\w+)/$ [name='registration_activate']
    # ^accounts/ ^register/$ [name='registration_register']
    # ^accounts/ ^register/complete/$ [name='registration_complete']
    # ^accounts/ ^register/closed/$ [name='registration_disallowed']
    # ^accounts/ ^password/change/$ [name='auth_password_change']
    # ^accounts/ ^password/change/done/$ [name='auth_password_change_done']
    # ^accounts/ ^password/reset/$ [name='auth_password_reset']
    # ^accounts/ ^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$ [name='auth_password_reset_confirm']
    # ^accounts/ ^password/reset/complete/$ [name='auth_password_reset_complete']
    # ^accounts/ ^password/reset/done/$ [name='auth_password_reset_done']
    #url(r'^accounts/login/$', 'accounts.views.login_mod', name='login_mod'),
    #url(r'^accounts/register/$', 'registration.views.register', {'backend': 'registration.backends.default.DefaultBackend',
    #    'form_class': CustomEmailRegistrationForm}, name='registration_register'),
    #url(r'^accounts/', include('registration_email.backends.default.urls')),
    #url(r'^doc/tos/$', 'filopod.views.tos', name='tos'),
    #url(r'^doc/privacy/$', 'filopod.views.privacy', name='privacy'),
    #url(r'^doc/publishers/$', 'filopod.views.publishers', name='publishers'),
        
    #url(r'^main/profile/$', 'main.views.profile', name='user_profile'),
    #url(r'^main/respacks/$', 'main.views.respacks', name='res_packages'),
    #url(r'^main/respacks/add', 'main.views.respacks_user_add', name='respacks_user_add'),
    #url(r'^main/respacks/remove', 'main.views.respacks_user_remove', name='respacks_user_remove'),
    #url(r'^main/manage/$', 'main.views.manage', name='manage_resources'),
    #url(r'^main/bill/$', 'main.views.bill', name='bill'),
    #url(r'^main/manage_viewsubres', 'main.views.manage_viewsubres', name='manage_viewsubres'),
    #url(r'^main/exploration/$', 'main.views_exploration.exploration', name='exploration'),
    
    #url(r'^main/install', 'main.views.install', name='install'),
    #url(r'^main/help', 'main.views.help', name='help'),
    #url(r'^main/about/requestjournal/$', 'main.views.requestjournal', name='requestjournal'),
    #url(r'^main/about', 'main.views.about', name='about'),
    #url(r'^main/contact/feedback/$', 'main.views.contact_feedback', name='contact_feedback'),
    #url(r'^main/contact/support/$', 'main.views.contact_support', name='contact_support'),
        
    # urls for exploration ajax calls
    #url(r'^get_concept_types', 'main.views_exploration.get_concept_types', name='get_concept_types'),
    #url(r'^selection_autocomplete', 'main.views_exploration.selection_autocomplete', name='selection_autocomplete'),
    #url(r'^network_graph_data', 'main.views_exploration.network_graph_data', name='network_graph_data'),
    #url(r'^fetch_resources', 'main.views_exploration.fetch_resources', name='fetch_resources'),
)
