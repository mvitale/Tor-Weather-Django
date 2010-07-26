"""The urls.py module is standard to Django. It stores url patterns and their
corresponding controllers (see views).

@var urlpatterns: A set of tuples mapping url patterns to the controller they
    should call.
"""

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'weatherapp.views.home'),
    (r'^subscribe/$', 'weatherapp.views.subscribe'),
    (r'^pending/(?P<confirm_auth>.+)/$', 'weatherapp.views.pending'),
    (r'^confirm/(?P<confirm_auth>.+)/$', 'weatherapp.views.confirm'),
    (r'^unsubscribe/(?P<unsubscribe_auth>.+)/$',
                        'weatherapp.views.unsubscribe'),
    (r'^preferences/(?P<pref_auth>.+)/$',
                        'weatherapp.views.preferences'),
    (r'^confirm_pref/(?P<pref_auth>.+)/$',
                        'weatherapp.views.confirm_pref'),
    (r'^fingerprint_not_found/(?P<fingerprint>.+)/$',
                        'weatherapp.views.fingerprint_not_found'),
    (r'^error/(?P<error_type>[a-z_]+)/(?P<key>.+)/$', 
                        'weatherapp.views.error'),
    (r'^resend_conf/(?P<confirm_auth>.+)/$', 
                        'weatherapp.views.resend_conf'),
    (r'^notification_info/$', 'weatherapp.views.notification_info'),
    (r'^router_name_lookup/$', 
                        'weatherapp.views.router_name_lookup'),
    (r'^router_fingerprint_lookup/$',
                        'weatherapp.views.router_fingerprint_lookup'),
    
    # This is for serving static files for the development server, mainly for
    # getting the CSS file and jquery file.
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': 'media'}),
)
