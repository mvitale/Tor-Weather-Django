from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('weather.weatherapp.views',
    (r'^$', 'home'),
    (r'^subscribe/$', 'subscribe'),
    (r'^pending/(?P<confirm_auth>.+)/$', 'pending'),
    (r'^confirm/(?P<confirm_auth>.+)/$', 'confirm'),
    (r'^unsubscribe/(?P<unsubscribe_auth>.+)/$','unsubscribe'),
    (r'^preferences/(?P<pref_auth>.+)/$','preferences'),
    (r'^confirm_pref/(?P<pref_auth>.+)/$','confirm_pref'),
    (r'^fingerprint_error/(?P<fingerprint>.+)/$', 
                                                'fingerprint_error'),
    (r'^error/(?P<error_type>[a-z_]+)/(?P<subscriber_id>\d+)/$', 'error'),
    (r'^run_updaters$', 'run_updaters'),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
