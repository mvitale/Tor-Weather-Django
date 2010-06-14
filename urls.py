from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('weather.weatherapp.views',
    (r'^$', 'subscribe'),
    (r'^pending/(?P<subscriber_id>\d+)/$', 'pending'),
    (r'^confirm/(?P<confirm_auth_id>[a-zA-Z0-9]+)/$', 'confirm'),
    (r'^unsubscribe/(?P<unsubscribe_auth_id>[a-zA-Z0-9]+)/$','unsubscribe'),
    (r'^preferences/(?P<preferences_auth_id>[a-zA-Z0-9]+)/$','preferences'),
    (r'^confirm_pref/(?P<preferences_auth_id>[a-zA-Z0-9]+)/$','confirm_pref'),
    (r'^fingerprint_error/(?P<fingerprint>[a-zA-Z0-9]+)/$', 
                                                'fingerprint_error'),
    (r'^runpoller$', 'runpoller'),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
