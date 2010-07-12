"""This module contains the different error messages that may be displayed to 
the user via the web pages and the method to access the correct message.

@var _ALREADY_CONFIRMED: The error message displayed when the user attempts
    to confirm his/her subscription more than once by following the link sent
    to them via email. The message contains a link to the user's preferences
    and a link to unsubscribe.
@var _ALREADY_SUBSCRIBED: The error message displayed when the user attempts to
    subscribe to a particular node he/she is already subscribed to. The message
    contains a link to the user's preferences page.
@var _NEED_CONFIRMATION: The error message displayed when the user attempts to
    change his/her preferences before confirming the subscription.
@var _DEFAULT: This message is displayed if the url pattern following /error/ 
    is not recognized by the get_error_message method.
"""
    
from weather.weatherapp.models import Subscriber
from weather.config import url_helper

_ALREADY_CONFIRMED = "<p>You have already confirmed your Tor Weather " +\
    "subscription. The link you followed is no longer functional. " +\
    "</p><p>You can change your preferences by following this link: " +\
    "<br /><a href=%s>%s</a></p>" +\
    "<p>You can unsubscribe at any time here:" +\
    "<br><a href=%s>%s</a></p>"
_ALREADY_SUBSCRIBED = "<p>You are already subscribed to receive email " +\
    "alerts about the node you specified.</p><p>If you'd like, you can " +\
    " <a href = '%s'>change your preferences here</a>.</p>"
_NEED_CONFIRMATION ="<p>You have not yet confirmed your subscription to Tor "+\
    "Weather. You should have received an email at %s from Tor Weather "+\
    "with a link to your confirmation page.</p><p>If you would like us "+\
    "to resend the email with a link to your confirmation page, "+\
    "<a href=%s>click here</a>.</p>"
_DEFAULT = "Tor Weather has encountered an error in trying to redirect "+\
    "to this page."

def get_error_message(error_type, key):
    """Returns an error message based on the error type and user-specific
    key. The error message contains HTML formatting and should be
    incorporated into the template for the error page.

    @type error_type: str
    @param error_type: The type of error.
    @type key: str
    @param key: A key that provides user-specific or error-specific
        information for error message generation.
    """
    message = ""
    if error_type == 'already_confirmed':
        confirm_auth = key
        user = Subscriber.objects.get(confirm_auth = confirm_auth)
        pref_url = url_helper.get_preferences_url(user.pref_auth)
        unsubscribe_url = url_helper.get_unsubscribe_url(user.unsubs_auth)
        message = _ALREADY_CONFIRMED % (pref_url, pref_url, 
                                                      unsubscribe_url,
                                                      unsubscribe_url)
        return message
    elif error_type == 'already_subscribed':
        # the key represents the user's pref_auth key
        pref_auth = key
        pref_url = url_helper.get_preferences_url(pref_auth)
        message = _ALREADY_SUBSCRIBED % pref_url
        return message
    elif error_type == 'need_confirmation':
        # the key represents the user's confirm_auth key
        confirm_auth = key
        user = Subscriber.objects.get(confirm_auth = confirm_auth)
        url_extension = url_helper.get_resend_ext(confirm_auth)
        message = _NEED_CONFIRMATION % (user.email, 
                                                      url_extension)
        return message
    else:
        # the error type wasn't recognized, just return a default msg
        message = _DEFAULT
        return message

