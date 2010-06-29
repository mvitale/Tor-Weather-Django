"""The urls.py module is standard to Django. It stores url patterns and their
corresponding controllers (see views).

@var urlpatterns: A set of tuples mapping url patterns to the controller they
    should call.
"""

<<<<<<< HEAD:urls.py
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
=======
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()
urlpatterns = patterns('',
    (r'^$', 'weather.weatherapp.views.home'),
    (r'^subscribe/$', 'weather.weatherapp.views.subscribe'),
    (r'^pending/(?P<confirm_auth>.+)/$', 'weather.weatherapp.views.pending'),
    (r'^confirm/(?P<confirm_auth>.+)/$', 'weather.weatherapp.views.confirm'),
    (r'^unsubscribe/(?P<unsubscribe_auth>.+)/$',
                        'weather.weatherapp.views.unsubscribe'),
    (r'^preferences/(?P<pref_auth>.+)/$',
                        'weather.weatherapp.views.preferences'),
    (r'^confirm_pref/(?P<pref_auth>.+)/$',
                        'weather.weatherapp.views.confirm_pref'),
    (r'^fingerprint_not_found/(?P<fingerprint>.+)/$',
                        'weather.weatherapp.views.fingerprint_not_found'),
    (r'^error/(?P<error_type>[a-z_]+)/(?P<key>.+)/$', 
                        'weather.weatherapp.views.error'),
    (r'^resend_conf/(?P<confirm_auth>.+)/$', 
                        'weather.weatheapp.views.resend_conf'),
    (r'^run_updaters$', 'weather.weatherapp.views.run_updaters'),

    # This is for serving static files for the development server, mainly for
    # getting the CSS file and jquery file.
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': '/home/jruberg/code/weather/media'}),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
>>>>>>> subprototype:urls.py
)
