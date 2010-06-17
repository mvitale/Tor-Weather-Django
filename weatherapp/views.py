"""
The views module contains the controllers for the Tor Weather application 
(Django is idiosyncratic in that it names controllers 'views'; models are still
models and views are called templates). This module contains a single 
controller for each page type. The controllers handle form submission and
page rendering/redirection.
"""
from models import Subscriber, Subscription, Router, \
                   SubscribeForm, PreferencesForm
from django.db import models
from django.shortcuts import render_to_response, get_object_or_404
import emails
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
    subscribe = '/subscribe/' 
# --------------- Change this later so it isn't hard coded -------------
    return render_to_response('home.html', {'sub' : subscribe})

def subscribe(request):
    """Displays the subscription form (all fields empty or default) if the
    form hasn't been submitted. After the user hits the submit button,
    redirects to the pending page if all of the fields were acceptable.
    If the user enters a fingerprint that isn't stored in our database,
    we send them to an error page (see L{fingerprint_error}). If the user
    is already subscribed to that Tor node, they are sent to an error page."""
    
    if request.method == 'POST':
        # handle the submitted form:
        form = SubscribeForm(request.POST)

# -----------------------------------------------------------------------
# NEED TO CHECK HOW DJANGO CHECKS IF AN EMAIL FIELD IS VALID ------------
# -----------------------------------------------------------------------
        if form.is_valid():
            addr = form.cleaned_data['email']
            fingerprint = form.cleaned_data['fingerprint']
            grace_pd = form.cleaned_data['grace_pd']
            
            router_primary_key = 0
            # this will store the router's primary key, which we need to add
            # the subscriber to the database
            try:
                router = Router.objects.get(fingerprint = fingerprint)
                router_primary_key = router.id
            except Router.DoesNotExist:
                return HttpResponseRedirect('/fingerprint_error/' +\
                    fingerprint + '/')

            try:
                user = Subscriber.objects.get(router=router_primary_key)
                # if no error is raised, the user is already subscribed to
                # this router, so we redirect them.
                return HttpResponseRedirect('/error/already_subscribed/'+\
                    user.id+'/')
# ---------------------------------------------------------------------
#   Should redirect to a specific error page (already subscribed)
# ---------------------------------------------------------------------
            except Subscriber.DoesNotExist:
                # the user isn't subscribed yet, send the email & add them
                pass 
                      
            e = Emailer()
# ---------------------------------------------------------------------
#  make sure the method name is correct for sending the email
# ---------------------------------------------------------------------
            e.send_confirmation(addr, fingerprint, user.confirm_auth)
            
            # Create the subscriber model for the user
            user = Subscriber(email=addr, router=router_primary_key)
            # Save the subscriber data to the database
            user.save()
            # Create the node_down subscription and save to db
            subscription = Subscription(subscriber=user, name='node_down', 
                grace_pd=grace_pd)
            subscription.save()
            # send the user to the pending page
            return HttpResponseRedirect('/pending/'+user.id+'/')
    else:
        # user hasn't submitted info, just display the empty subscribe form
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
    rout = Router.objects.get(pk=sub.router)
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
            grace_pd = form.cleaned_data['grace_pd']
            user = get_object_or_404(Subscriber, pref_auth = 
                preferences_auth_id)
            # get the node down subscription so we can update grace_pd
            node_down_sub = get_object_or_404(Subscription, subscriber = user,
                name = node_down)
            node_down_sub.update(grace_pd = grace_pd)
            return HttpResponseRedirect('confirm_pref/'+preferences_auth_id+'/',
                    preferences_auth_id) 

    #the user hasn't submitted the form yet or submitted it incorrectly, 
    # so the page with the preferences form is displayed.

    # get the user
    user = get_object_or_404(Subscriber, pref_auth = preferences_auth_id)
    # get the node down subscription 
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

def error(request, error_type, user_id):
    """The generic error page, which displays a message based on the error
    type passed to this controller."""
    
    #user = get_object_or_404(Subscriber, id=user_id)
    __ALREADY_SUBSCRIBED = "You are already subscribed to receive email" +\
        "alerts about the node you specified. If you'd like, you can" +\
        " <a href = '%s'>change your preferences here</a>" % baseURL #+\
        #'/preferences/' + user.pref_auth + '/'
#----------------------------------------------------------------------
# FIX THIS LINK STUFF
#----------------------------------------------------------------------

    if error_type == already_subscribed:
        message = __ALREADY_SUBSCRIBED
    return render_to_response('error.html', {'error_message' : message})

def run_updaters(request):
    """
    Runs all updaters when the appropriate request is made from localhost.
    If any other ip tries to do this, displays 404 error.
    """

    client_address = request.META['REMOTE_ADDR'] 

    #Only allow localhost to make this request.
    #We need to make sure this works!!!
    if client_address == "127.0.0.1":
        updaters.run_all() 
    else:
        raise Http404

    return HttpResponse()
