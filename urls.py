from django.conf.urls.defaults import *

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
    (r'^fingerprint_error/(?P<fingerprint>.+)/$', 
                        'weather.weatherapp.views.fingerprint_error'),
    (r'^error/(?P<error_type>[a-z_]+)/(?P<subscriber_id>\d+)/$', 
                        'weather.weatherapp.views.error'),
    (r'^run_updaters$', 'weather.weatherapp.views.run_updaters'),

    # This is for serving static files for the development server, mainly for
    # getting the CSS file.
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': '/home/jruberg/code/weather/media'}),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
