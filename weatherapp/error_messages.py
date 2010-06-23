from weather.weatherapp.models import Subscriber

class ErrorMessages:
    """The ErrorMessages class contains the different error messages that 
    may be displayed to the user via the web pages.
    """

    _ALREADY_CONFIRMED = "You have already confirmed your Tor Weather " +\
        "subscription. The link you followed is no longer functional. " +\
        "</p><p>You can change your preferences by following this link: " +\
        "<br>%s</p><p>You can unsubscribe at any time here:<br>%s</p>"
    _ALREADY_SUBSCRIBED = "You are already subscribed to receive email " +\
        "alerts about the node you specified. If you'd like, you can " +\
        " <a href = '%s'>change your preferences here</a>." 
    _FINGERPRINT_NOT_FOUND = "We could not locate a Tor node with " +\
        "fingerprint %s.</p><p>Here are some potential problems:" +\
        "<ul><li>The fingerprint was entered incorrectly</li>" +\
        "<li>The node with the given fingerprint was set up within the last "+\
        "hour, in which case you should try to register again a bit later" +\
        "</li><li>The node with the given fingerprint has been down for over "+\
        "a year"
    _NEED_CONFIRMATION ="You have not yet confirmed your subscription to Tor "+\
        "Weather. You should have received an email from Tor Weather with "+\
        "a link to your confirmation page."
# ---------------- BUTTON TO SEND THE EMAIL AGAIN!! -------------------
    _DEFAULT = "Tor Weather has encountered an error."

    @staticmethod
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
            pref_url = Urls.get_preferences_url(user.pref_auth)
            unsubscribe_url = Urls.get_unsubscribe_url(user.unsubs_auth)
            message = ErrorMessages._ALREADY_CONFIRMED % (pref_url, 
                                                          unsubscribe_url)
            return message
        elif error_type == 'already_subscribed':
            # the key represents the user's pref_auth key
            pref_auth = key
            pref_url = Urls.get_preferences_url(pref_auth)
            message = ErrorMessages._ALREADY_SUBSCRIBED % pref_url
            return message
        elif error_type == 'fingerprint_not_found':
            # the key represents the fingerprint the user tried to enter
            fingerprint = key
            message = ErrorMessages._FINGERPRINT_NOT_FOUND % fingerprint
            return message
        elif error_type == 'need_confirmation':
            message = ErrorMessages._NEED_CONFIRMATION
            return message
        else:
            # the error type wasn't recognized, just return a default msg
            message = ErrorMessages._DEFAULT
            return message

