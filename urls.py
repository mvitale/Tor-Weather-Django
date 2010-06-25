"""The urls.py module is standard to Django. It stores url patterns and their
corresponding controllers (see views).

@var urlpatterns: A set of tuples mapping url patterns to the controller they
    should call.
"""

from django.conf.urls.defaults import *

urlpatterns = patterns('weather.weatherapp.views',
    (r'^$', 'home'),
    (r'^subscribe/$', 'subscribe'),
    (r'^pending/(?P<confirm_auth>.+)/$', 'pending'),
    (r'^confirm/(?P<confirm_auth>.+)/$', 'confirm'),
    (r'^unsubscribe/(?P<unsubscribe_auth>.+)/$','unsubscribe'),
    (r'^preferences/(?P<pref_auth>.+)/$','preferences'),
    (r'^confirm_pref/(?P<pref_auth>.+)/$','confirm_pref'),
    (r'^fingerprint_not_found/(?P<fingerprint>.+)/$', 
                                                'fingerprint_not_found'),
    (r'^error/(?P<error_type>[a-z_]+)/(?P<key>.+)/$', 'error'),
    (r'^resend_conf/(?P<confirm_auth>.+)/$', 'resend_conf'),
    (r'^run_updaters$', 'run_updaters'),
)
