"""
The views module contains the controllers for the Tor Weather application 
(Django is idiosyncratic in that it names controllers 'views'; models are still
models and views are called templates). This module contains a single 
controller for each page type. The controllers handle form submission and
page rendering/redirection.
"""
import threading

from weatherapp.models import Subscriber, NodeDownSub, Router, \
                   GenericForm, SubscribeForm, PreferencesForm
import emails
import error_messages
from config import url_helper, templates

import django.views.static
from django.db import models
from django.core.context_processors import csrf
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpRequest, Http404
from django.http import HttpResponse
from weather.weatherapp import error_messages

# TO DO --------------------------------------------------------- EXTRA FEATURE
# MOVE THIS TO A MORE GENERAL LOCATION ----------------------------------------
baseURL = "http://localhost:8000"

def home(request):
    """Displays a home page for Tor Weather with basic information about
    the application."""
    url_extension = url_helper.get_subscribe_ext()
    return render_to_response(templates.home, {'sub' : url_extension})

def subscribe(request):
    """Displays the subscription form (all fields empty or default) if the
    form hasn't been submitted. After the user hits the submit button,
    redirects to the pending page if all of the fields were acceptable.
    If the user is already subscribed to that Tor node, they are sent to 
    an error page."""
    
    if request.method == 'POST':
        # Replaces fields in POST data of the form 'Default value is ---' with
        # just the integer value, so that the to_python() methods of the 
        # form validation don't go crazy.
        request.POST = GenericForm.clean_post_data(request.POST)
        
        # handle the submitted form:
        form = SubscribeForm(request.POST)

        if form.is_valid():
            # Tries to save the new subscriber, but redirects if saving the
            # subscriber failed because of the subscriber already existing
            try:
                subscriber = form.save_subscriber()
            except Exception, e:
                return HttpResponseRedirect(e)
            else:
                form.save_subscriptions(subscriber)

                # Spawn a daemon to send the confirmation email.
                confirm_auth = subscriber.confirm_auth
                addr = subscriber.email
                fingerprint = subscriber.router.fingerprint
                email_thread = threading.Thread(
                        target=emails.send_confirmation,
                        args=[addr, fingerprint, confirm_auth])
                email_thread.setDaemon(True)
                email_thread.start()
        
                # Redirect the user to the pending page.
                url_extension = url_helper.get_pending_ext(confirm_auth)
                return HttpResponseRedirect(url_extension)
    else:
        # User hasn't submitted info, so just display empty subscribe form.
        form = SubscribeForm()
    c = {'form' : form}

    # For pages with POST methods, a Cross Site Request Forgery protection
    # key is added to block attacking sites.
    c.update(csrf(request))

    return render_to_response(templates.subscribe, c)

def notification_info(request):
    """Displays detailed technical information about how the different
    notification types are triggered.
    """

    return render_to_response(templates.notification_info)


def pending(request, confirm_auth):
    """The user views the pending page after submitting a registration form.
    The page tells the user that a confirmation email has been sent to 
    the address the user provided.
    
    @type confirm_auth: str
    @param confirm_auth: The user's confirmation authorization key.
    """
    user = get_object_or_404(Subscriber, confirm_auth=confirm_auth)

    if not user.confirmed:
        return render_to_response(templates.pending, {'email': user.email})

    # Redirects to the home page if the user has already confirmed
    url_extension = url_helper.get_home_ext()
    return HttpResponseRedirect(url_extension)

def confirm(request, confirm_auth):
    """The confirmation page, which is displayed when the user follows the
    link sent to them in the confirmation email.
    
    @type confirm_auth: str
    @param confirm_auth: The user's confirmation authorization key.
    """
    user = get_object_or_404(Subscriber, confirm_auth=confirm_auth)
    router = user.router

    if not user.confirmed:
        # confirm the user's subscription
        user.confirmed = True
        user.save()
    else:
        # the user is already confirmed, send to an error page
        error_url_ext = url_helper.get_error_ext('already_confirmed',    
                                                 confirm_auth)
        return HttpResponseRedirect(error_url_ext)

    # get the urls for the user's unsubscribe and prefs pages to add links
    unsubURL = url_helper.get_unsubscribe_url(user.unsubs_auth)
    prefURL = url_helper.get_preferences_url(user.pref_auth)

    # spawn a daemon to send an email confirming subscription and 
    #providing the links
    email_thread=threading.Thread(target=emails.send_confirmed,
                            args=[user.email, router.fingerprint, 
                                  user.unsubs_auth, user.pref_auth])
    email_thread.setDaemon(True)
    email_thread.start()

    # get the template for the confirm page
    template = templates.confirm

    return render_to_response(template, {'email': user.email, 
                                         'fingerprint' : router.fingerprint, 
                                         'nodeName' : router.name, 
                                         'unsubURL' : unsubURL, 
                                         'prefURL' : prefURL})
        
def unsubscribe(request, unsubscribe_auth):
    """The unsubscribe page, which displays a message informing the user
    that they will no longer receive emails at their email address about
    the given Tor node.
    
    @type unsubscribe_auth: str
    @param unsubscribe_auth: The user's unsubscribe authorization key.
    """
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
    url_extension = url_helper.get_subscribe_ext()
    # get the unsubscribe template
    template = templates.unsubscribe
    return render_to_response(template, {'email' : email, 
                                         'name' : name,
                                         'fingerprint' :fingerprint, 
                                         'subURL': url_extension})

def preferences(request, pref_auth):
    """The preferences page, which contains the preferences form initially
    populated by user-specific data
    
    @type pref_auth: str
    @param pref_auth: The user's preferences authorization key.
    """
    user = get_object_or_404(Subscriber, pref_auth=pref_auth)
    if not user.confirmed:
        # the user hasn't confirmed, send them to an error page
        error_extension = url_helper.get_error_ext('need_confirmation', 
                                             user.confirm_auth)
        return HttpResponseRedirect(error_extension)
    if request.method == "POST":
        # The user submitted the preferences form and is redirected to the 
        # confirmation page.
        form = PreferencesForm(request.POST)
        if form.is_valid():
            grace_pd = form.cleaned_data['grace_pd']

            # Get the node_down subscription so we can update grace_pd.
            node_down_sub = get_object_or_404(NodeDownSub, subscriber = user)
            node_down_sub.grace_pd = grace_pd
            node_down_sub.save()

            url_extension = url_helper.get_confirm_pref_ext(pref_auth)
            return HttpResponseRedirect(url_extension) 

    # TO DO ----------------------------------------------------- EXTRA FEATURE
    # SHOULD IMPLEMENT ERROR MESSAGES THAT SAY THE FORM IS --------------------
    # SPECIFIED INCORRECTLY ---------------------------------------------------

    # The user hasn't submitted the form yet or submitted it incorrectly, 
    # so the page with the preferences form is displayed.

    else:
    # the user hasn't submitted the form yet, display blank page
        
        # get the node down subscription 
        node_down_sub = get_object_or_404(NodeDownSub, subscriber = user)
                
        # the data is used to fill in the form on the preferences page
        # with the user's existing preferences.    
        # this should be updated as the preferences are expanded
        data = {'grace_pd' : node_down_sub.grace_pd}

        # populates a PreferencesForm object with the user's existing prefs.
        form = PreferencesForm(initial=data)    
    
    # maps the form to the template.
    c = {'pref_auth': pref_auth, 'fingerprint': user.router.fingerprint,
         'form' : form}

    # Creates a CSRF protection key.
    c.update(csrf(request))

    # get the template
    template = templates.preferences
    # display the page
    return render_to_response(template, c)

def confirm_pref(request, pref_auth):
    """The page confirming that preferences have been changed.
    
    @type pref_auth: str
    @param pref_auth: The user's preferences authorization key.
    """
    user = get_object_or_404(Subscriber, pref_auth = pref_auth)
    prefURL = url_helper.get_preferences_url(pref_auth)
    unsubURL = url_helper.get_unsubscribe_url(user.unsubs_auth)

    # get the template
    template = templates.confirm_pref

    # The page includes the unsubscribe and change prefs links
    return render_to_response(template, {'prefURL' : prefURL,
                                         'unsubURL' : unsubURL})

def resend_conf(request, confirm_auth):
    """The page informing the user that the confirmation email containing
    the link to finalize the subscription has been resent.
    
    @type confirm_auth: str
    @param confirm_auth: The user's confirmation authorization key.
    """
    user = get_object_or_404(Subscriber, confirm_auth = confirm_auth)
    router = user.router
    template = templates.resend_conf

    # spawn a daemon to resend the confirmation email
    email_thread=threading.Thread(target=emails.send_confirmation,
                            args=[user.email, router.fingerprint, confirm_auth])
    email_thread.setDaemon(True)
    email_thread.start()

    return render_to_response(template, {'email' : user.email})


def fingerprint_not_found(request, fingerprint):
    """Displays the fingerprint not found page when a user follows a link for 
    more info in the 'fingerprint not found' validation error. This error is 
    displayed on the subscribe form if the user tries to subscribe to a node 
    that isn't in our database.

    @type fingerprint: str
    @param fingerprint: The fingerprint the user entered in the subscribe form.
    """
    # get the template
    template = templates.fingerprint_not_found

    #display the page
    return render_to_response(template, {'fingerprint' : fingerprint})

def error(request, error_type, key):
    """The generic error page, which displays a message based on the error
    type passed to this controller.
    
    @type error_type: str
    @param error_type: A description of the type of error encountered.
    @type key: str
    @param key: A key interpreted by the get_error_message function in the 
        error_messages module to render a user-specific error message."""
    
    # get the appropriate error message
    message = error_messages.get_error_message(error_type, key)

    # get the error template
    template = templates.error

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
