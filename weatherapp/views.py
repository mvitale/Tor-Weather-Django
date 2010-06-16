"""
The views module contains the controllers for the Tor Weather application 
(Djago is idiosyncratic in that it names controllers 'views'; models are still
models and views are called templates). This module contains a single 
controller for each page type. The controllers handle form submission and
page rendering/redirection.
"""

from django.shortcuts import render_to_response, get_object_or_404
from weather.weatherapp.models import Subscriber, Subscription, Router
from weather.weatherapp.models import SubscribeForm, PreferencesForm
from weather.weatherapp.helpers import Emailer
from django.core.context_processors import csrf
from django.http import HttpResponseRedirect, HttpRequest, Http404
from django.http import HttpResponse

# -----------------------------------------------------------------------
# FILL IN ONCE WE KNOW THE SITE! ----------------------------------------
# -----------------------------------------------------------------------
baseURL = "http://localhost:8000"

def home(request):
    """Displays a home page for Tor Weather with basic information about
        the application."""
    subURL = baseURL + '/subscribe/'
    return render_to_response('home.html', {'subURL' : subURL})

def subscribe(request):
    """Displays the subscription form (all fields empty or default) if the
        form hasn't been submitted. After the user hits the submit button,
        redirects to the pending page if all of the fields were acceptable"""
    if request.method == 'POST':
        form = SubscribeForm(request.POST)

# -----------------------------------------------------------------------
# NEED TO CHECK HOW DJANGO CHECKS IF AN EMAIL FIELD IS VALID ------------
# -----------------------------------------------------------------------
        if form.is_valid():
            addr = form.cleaned_data['email']
            fingerprint = form.cleaned_data['fingerprint']
            grace_pd = form.cleaned_data['grace_pd']
            
            e = Emailer()
            e.send_single_email(addr, "confirmation")

            # Add subscriber to the database
# ---------------------------------------------------------------------- 
# NEEDS TO CHECK IF THERE IS A ROUTER IN DB WITH SPECIFIED FINGERPRINT
# AND IF THERE ISN'T SEND THEM TO AN ERROR PAGE, BUT IF THERE IS GET THE
# ROUTER ID AND THEN USE THAT AS A PARAMETER FOR ADD_NEW_SUBSCRIBER
# ----------------------------------------------------------------------
            # subscriber = Subscriber.add_new_subscriber() 
            
            return HttpResponseRedirect('/pending/'+subscriber.id+'/')
    else:
	form = SubscribeForm()
	c = {'form' : form}

	# for pages with POST methods, a Cross Site Request Forgery protection
	# key is added to block attacking sites
	c.update(csrf(request))
    return render_to_response('subscribe.html', c)

def pending(request, subscriber_id):
    """The user views the pending page after submitting a registration form.
        The page tells the user that a confirmation email has been sent to 
        the address the user provided."""
    user = get_object_or_404(Subscriber, pk=subscriber_id)
    if user.confirmed == false:
        return render_to_response('pending.html', {'email': sub.email})
    #returns the user to the home page if the subscriber has already confirmed
    return HttpResponseRedirect('/$')

def confirm(request, confirm_auth_id):
    """The confirmation page, which is displayed when the user follows the
        link sent to them in the confirmation email"""
    sub = get_object_or_404(Subscriber, confirm_auth=confirm_auth_id)
    rout = Router.objects.get(pk=sub.router_id)
    unsubURL = baseURL + "/unsubscribe/" + suber.unsubs_auth + "/"
    prefURL = baseURL + "/preferences/" + suber.pref_auth + "/"
    return render_to_response('confirm.html', {'email': sub.email, 
            'fingerprint' : rout.fingerprint, 'nodeName' : rout.name, 
            'unsubURL' : unsubURL, 'prefURL' : prefURL})
        
def unsubscribe(request, unsubscribe_auth_id):
    """The unsubscribe page, which displays a message informing the user
    that they will no longer receive emails at their email address about
    the given Tor node."""
    
    #get the user and router
    user = get_object_or_404(Subscriber, unsubs_auth = unsubscribe_auth_id)
    router = get_object_or_404(Router, pk = user.router)
    
    email = user.email
    router_name = router.name
    fingerprint = router.fingerprint 
    
    #we know the router has a fingerprint, but it might not have a name.
    name = ""
    if not router_name.equals("Unnamed"):
        name += " " + router_name + ","

    return render_to_response('unsubscribe.html', {'email' : email, 'name' : 
            name, 'fingerprint' : fingerprint})

def preferences(request, preferences_auth_id):
    """The preferences page, which contains the preferences form initially
        populated by user-specific data"""
    if request.method == "POST":
        #the user submitted the preferences form and is redirected to the
        #confirmation page.
        form = PreferencesForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('confirm_pref/'+preferences_auth_id+'/',
                    preferences_auth_id) 
    else:
        #the user hasn't submitted the form yet, so the page with the 
        #preferences form is displayed.
        user = get_object_or_404(Subscriber, pref_auth = preferences_auth_id)
        node_down_sub = get_object_or_404(Subscription, subscriber = user, 
                    name = node_down)

        # the data is used to fill in the form on the preferences page 
        # with the user's existing preferences.    
        # this should be updated as the preferences are expanded
        data = {'grace_pd' : node_down_sub.grace_pd}

	# populates a PreferencesForm object with the user's existing prefs
	form = PreferencesForm(initial=data)	
	
	# maps the form to the template
	c = {'form' : form}

	# Creates a CSRF protection key
	c.update(csrf(request))
    return render_to_response('preferences.html', c)

def confirm_pref(request, preferences_auth_id):
    """The page confirming that preferences have been changed."""
    prefURL = baseURL + '/preferences/' + preferences_auth_id + '/'
    user = get_object_or_404(Subscriber, pref_auth = preferences_auth_id)
    unsubURL = baseURL + '/unsubscribe/' + user.unsub_auth + '/'

    # The page includes the unsubscribe and change prefs links
    return render_to_response('confirm_pref.html', {'prefURL' : prefURL,
            'unsubURL' : unsubURL})

def fingerprint_error(request, fingerprint):
    """The page that is displayed when a user tries to subscribe to a node
    that isn't stored in the database. The page includes information
    regarding potential problems."""
    return render_to_response('fingerprint_error.html', {'fingerprint' :
        fingerprint})

def run_updaters(request):
    client_address = request.META['REMOTE_ADDR'] 
    if client_address == "127.0.0.1":
        updaters.run_all() 
    else:
        raise Http404
    return HttpResponse()
