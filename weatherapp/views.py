"""
The views module contains the controllers for the Tor Weather application 
(Django is idiosyncratic in that it names controllers 'views'; models are still
models and views are called templates). This module contains a single 
controller for each page type. The controllers handle form submission and
page rendering/redirection.
"""
from models import Subscriber, NodeDownSub, Router, \
                   SubscribeForm, PreferencesForm
from django.db import models
from django.shortcuts import render_to_response, get_object_or_404
from emails import Emailer
from django.core.context_processors import csrf
from django.http import HttpResponseRedirect, HttpRequest, Http404
from django.http import HttpResponse
from weather.config.web_directory import ErrorMessages, Templates, Urls

# TO DO --------------------------------------------------------- EXTRA FEATURE
# MOVE THIS TO A MORE GENERAL LOCATION ----------------------------------------
baseURL = "http://localhost:8000"

def home(request):
    """Displays a home page for Tor Weather with basic information about
        the application."""
    url_extension = Urls.get_subscribe_ext()
    return render_to_response(Templates.home, {'sub' : url_extension})

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

        # TO DO ------------------------------------------------- EXTRA FEATURE
        # CHECK HOW DJANGO CHECKS EMAIL FIELD, POSSIBLY -----------------------
        if form.is_valid():
            # gets the data from the form, ensuring the input conforms to the
            # types specified in the SubscribeForm object
            addr = form.cleaned_data['email']
            # gets the fingerprint and removes any whitespace characters
            fingerprint = form.cleaned_data['fingerprint'].replace(' ','')
            grace_pd = form.cleaned_data['grace_pd']
            
            # gets a query set of the routers with the given fingerprint
            # (there should be at most one).
            router_query_set = Router.objects.filter(fingerprint = fingerprint)
            
            if len(router_query_set) == 0:
            # we haven't seen this router before. display error page 
                
                #gets the url extension for the fingerprint error page
                url_extension = Urls.get_error_ext('fingerprint_not_found', 
                                                   fingerprint)
                return HttpResponseRedirect(url_extension)

            # the router is in the database, get the Router object
            router = router_query_set[0]

            user_query_set = Subscriber.objects.filter(email=addr,
                                                       router=router) 
            # if the Subscriber is in the set, the user is already subscribed 
            # to this router, so we redirect them.
            if len(user_query_set) > 0:
                user = user_query_set[0]

                if user.confirmed:
                    url_extension = Urls.get_error_ext('already_subscribed',
                                                       user.pref_auth)
                    return HttpResponseRedirect(url_extension)
                else:
                    url_extension = Urls.get_error_ext('need_confirmation',
                                                       user.conf_auth)
                    return HttpResponseRedirect(url_extension)
            
            # Create the subscriber model for the user.
            user = Subscriber(email=addr, router=router)

            # Save the subscriber data to the database.
            user.save()
            
# ---------------- Do this for every subscription --------------------------

            # Create the node down subscription and save to db.
            subscription = NodeDownSub(subscriber=user, grace_pd=grace_pd)
            subscription.save()
            
            # send the confirmation email
            confirm_auth = user.confirm_auth
            Emailer.send_confirmation(addr, fingerprint, confirm_auth)

            # Send the user to the pending page.
            url_extension = Urls.get_pending_ext(confirm_auth)
            return HttpResponseRedirect(url_extension)
    else:
        # User hasn't submitted info, so just display empty subscribe form.
        form = SubscribeForm()
    c = {'form' : form}

    # For pages with POST methods, a Cross Site Request Forgery protection
    # key is added to block attacking sites.
    c.update(csrf(request))

    return render_to_response(Templates.subscribe, c)

def pending(request, confirm_auth):
    """The user views the pending page after submitting a registration form.
        The page tells the user that a confirmation email has been sent to 
        the address the user provided."""
    user = get_object_or_404(Subscriber, confirm_auth=confirm_auth)

    if not user.confirmed:
        # TO DO ------------------------------------------------- EXTRA FEATURE
        return render_to_response(Templates.pending, {'email': user.email})

    # Returns the user to the home page if the subscriber has already confirmed
    url_extension = Urls.get_home_ext()
    return HttpResponseRedirect(url_extension)

def confirm(request, confirm_auth):
    """The confirmation page, which is displayed when the user follows the
        link sent to them in the confirmation email"""
    user = get_object_or_404(Subscriber, confirm_auth=confirm_auth)
    router = user.router

    if not user.confirmed:
        # confirm the user's subscription
        user.confirmed = True
    else:
        # the user is already confirmed, send to an error page
        error_url_ext = Urls.get_error_ext('already_confirmed', confirm_auth)
        return HttpResponseRedirect(error_url_ext)

    # get the urls for the user's unsubscribe and prefs pages to add links
    unsubURL = Urls.get_unsubscribe_url(user.unsubs_auth)
    prefURL = Urls.get_preferences_url(user.pref_auth)

    # send an email confirming subscription and providing the links
    Emailer.send_confirmed(user.email, router.fingerprint, unsubs_auth, 
                           pref_auth)

    # get the template for the confirm page
    template = Templates.confirm

    return render_to_response(template, {'email': user.email, 
                                         'fingerprint' : router.fingerprint, 
                                         'nodeName' : router.name, 
                                         'unsubURL' : unsubURL, 
                                         'prefURL' : prefURL})
        
def unsubscribe(request, unsubscribe_auth):
    """The unsubscribe page, which displays a message informing the user
    that they will no longer receive emails at their email address about
    the given Tor node."""
    
    # Get the user and router.
    user = get_object_or_404(Subscriber, unsubs_auth = unsubscribe_auth)
    router = user.router
    
    email = user.email
    router_name = router.name
    fingerprint = router.fingerprint 
    
    # We know the router has a fingerprint, but it might not have a name,
    # format the string.
    name = ""
    if router.name != "Unnamed":
        name += " " + router_name + ","

    # delete the Subscriber (all Subscriptions with a foreign key relationship
    # to this Subscriber are automatically deleted)
    user.delete()

    # get the url extension for the subscribe page to add a link on the page
    url_extension = Urls.get_subscribe_ext()
    # get the unsubscribe template
    template = Templates.unsubscribe
    return render_to_response(template, {'email' : email, 
                                         'name' : name,
                                         'fingerprint' :fingerprint, 
                                         'subURL': url_extension})

def preferences(request, pref_auth):
    """The preferences page, which contains the preferences form initially
        populated by user-specific data"""
# -------------- MAKE SURE THE USER IS CONFIRMED FIRST! --------------------
    if request.method == "POST":
        # The user submitted the preferences form and is redirected to the 
        # confirmation page.
        form = PreferencesForm(request.POST)
        if form.is_valid():
            grace_pd = form.cleaned_data['grace_pd']
            user = get_object_or_404(Subscriber, pref_auth =pref_auth)

            # Get the node_down subscription so we can update grace_pd.
            node_down_sub = get_object_or_404(NodeDownSub, subscriber = user)
            node_down_sub.grace_pd = grace_pd
            node_down_sub.save()

            url_extension = Urls.get_confirm_pref_ext(pref_auth)
            return HttpResponseRedirect(url_extension) 

    # TO DO ----------------------------------------------------- EXTRA FEATURE
    # SHOULD IMPLEMENT ERROR MESSAGES THAT SAY THE FORM IS --------------------
    # SPECIFIED INCORRECTLY ---------------------------------------------------

    # The user hasn't submitted the form yet or submitted it incorrectly, 
    # so the page with the preferences form is displayed.

    # get the user
    user = get_object_or_404(Subscriber, pref_auth = pref_auth)

    # get the user's router's fingerprint
    fingerprint = user.router.fingerprint

    # get the node down subscription 
    node_down_sub = get_object_or_404(NodeDownSub, subscriber = user)
                
    # the data is used to fill in the form on the preferences page
    # with the user's existing preferences.    
    # this should be updated as the preferences are expanded
    data = {'grace_pd' : node_down_sub.grace_pd}

    # populates a PreferencesForm object with the user's existing prefs.
    form = PreferencesForm(initial=data)    
    
    # maps the form to the template.
    c = {'pref_auth': pref_auth, 'fingerprint': fingerprint, 'form' : form}

    # Creates a CSRF protection key.
    c.update(csrf(request))

    # get the template
    template = Templates.preferences
    # display the page
    return render_to_response(template, c)

def confirm_pref(request, pref_auth):
    """The page confirming that preferences have been changed."""
    user = get_object_or_404(Subscriber, pref_auth = pref_auth)
    prefURL = Urls.get_preferences_url(pref_auth)
    unsubURL = Urls.get_unsubscribe_url(user.unsubs_auth)

    # get the template
    template = Templates.confirm_pref

    # The page includes the unsubscribe and change prefs links
    return render_to_response(template, {'prefURL' : prefURL,
                                         'unsubURL' : unsubURL})

# ------------------- REMOVE? --------------------------------------------

#def fingerprint_error(request, fingerprint):
#    """The page that is displayed when a user tries to subscribe to a node
#    that isn't stored in the database. The page includes information
#    regarding potential problems and references the fingerprint the user
#    entered into the form.
#    
#    @type fingerprint: str
#    @param fingerprint: The fingerprint the user entered in the subscribe form.
#    """
#    # get the template
#    template = Templates.fingerprint_error
#
#    #display the page
#    return render_to_response(template, {'fingerprint' : fingerprint})

# --------------------------------------------------------------------------

def error(request, error_type, key):
    """The generic error page, which displays a message based on the error
    type passed to this controller.
    
    @type error_type: str
    @param error_type: A description of the type of error encountered.
    @type key: str
    @param key: A key interpreted by the L{ErrorMessages} class to render
        a user-specific error message."""
    
    # get the appropriate error message
    message = ErrorMessages.get_error_message(error_type, key)

    # get the error template
    template = Templates.error

    # display the page
    return render_to_response(template, {'error_message' : message})

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
