"""
This module contains classes for accessing urls, html templates, and specific
error messages. The purpose of putting them all in a separate directory was for convenience of development. If the file/url extensions are ever changed, or
if the error messages need to be modified, the changes need only be made in
one place (here).
"""

base_url = 'http://localhost:8000'

# --------------------------------------------------------------------------
# CHANGE ONCE WE KNOW THE BASE URL
# --------------------------------------------------------------------------

class ErrorMessages:
    """The ErrorMessages class contains the different error messages that 
    may be displayed to the user via the web pages.
    """

    __ALREADY_SUBSCRIBED = "You are already subscribed to receive email" +\
        "alerts about the node you specified. If you'd like, you can" +\
        " <a href = '%s'>change your preferences here</a>" 
    __FINGERPRINT_NOT_FOUND = "We could not locate a Tor node with" +\
        "fingerprint %s.</p><p>Here are some potential problems:" +\
        "<ul><li>The fingerprint was entered incorrectly</li>" +\
        "<li>The node with the given fingerprint was set up within the last" +\
        "hour, in which case you should try to register again a bit later" +\
        "</li><li>The node with the given fingerprint has been down for over"+\
        "a year"
    __DEFAULT = "Tor Weather has encountered an error."

    def get_error_message(error_type, key):
        """Returns an error message based on the error type and user-specific
        key. The error message contains HTML formatting and should be
        incorporated into the template for the error page.

        @type error_type: str
        @param error_type: The type of error.
        """
        message = ""
        if error_type == 'already_subscribed':
            # the key represents the user's pref_auth key
            pref_auth = key
            pref_url = Urls.get_preferences_url(pref_auth)
            message = ErrorMessages.__ALREADY_SUBSCRIBED % pref_url
            return message
        elif error_type == 'fingerprint_not_found':
            # the key represents the fingerprint the user tried to enter
            fingerprint = key
            message = ErrorMessages.__FINGERPRINT_NOT_FOUND % fingerprint
            return message
        else:
            message = ErrorMessages.__DEFAULT
            return message

class Templates:
    """ The Templates class maps all of the html template files, which are
    stored in the templates directory, to instance variables for easier access 
    by the controllers (see views.py).

    @type confirm: str
    @ivar confirm: The template for the confirmation page. 
    @type confirm_pref: str
    @ivar confirm_pref: The template to confirm preferences have been changed.
    @type error: str
    @ivar error: The generic error template.
    @type fingerprint_error: str
    @ivar fingerprint_error: The template for the page displayed when a 
        fingerprint isn't found.
    @type home: str
    @ivar home: The template for the Tor Weather home page.
    @type pending: str
    @ivar pending: The template for the pending page displayed after the user 
        submits a subscription form.
    @type preferences: str
    @ivar preferences: The template for the page displaying the form to change 
        preferences.
    @type subscribe: str
    @ivar subscribe: The template for the page displaying the subscribe form.
    @type unsubscribe: str
    @ivar unsubscribe: The template for the page displayed when the user 
        unsubscribes from Tor Weather.
    """
    confirm = 'confirm.html'
    confirm_pref = 'confirm_pref.html'
    error = 'error.html'
    fingerprint_error = 'fingerprint_error.html'
    home = 'home.html'
    pending = 'pending.html'
    preferences = 'preferences.html'
    subscribe = 'subscribe.html'
    unsubscribe = 'unsubscribe.html'

class Urls:
    """The URLs class contains methods for accessing the Tor Weather urls and 
    url extensions.
    """

    __CONFIRM = '/confirm/%s/'
    __CONFIRM_PREF = '/confirm_pref/%s/'
    __ERROR = '/error/%s/%s/'
    __FINGERPRINT_ERROR = '/fingerprint_error/%s/'
    __HOME = '/'
    __PENDING = '/pending/%s/'
    __PREFERENCES = '/preferences/%s/'
    __SUBSCRIBE = '/subscribe/'
    __UNSUBSCRIBE = '/unsubscribe/%s/'

    @staticmethod
    def get_confirm_url(confirm_auth,
                        path = __CONFIRM):
        """Returns a string representation of the full url for the confirmation 
        page, which is sent to the user in an email after they subscribe.
    
        @type confirm_auth: str
        @param confirm_auth: The user's unique confirmation authorization key, 
            which is used to prevent inappropriate access of this page and to 
            access specific information about the user from the database 
            (email, unsubs_auth, and pref_auth) to be displayed on the 
            confirmation page. The key is incorporated into the url.
        @rtype: str
        @return: The user-specific confirmation url. 
        """
        url = base_url + path % confirm_auth
        return url

    @staticmethod
    def get_confirm_pref_ext(pref_auth,
                             path = __CONFIRM_PREF):
        """Returns the url extension for the page confirming the user's 
        submitted changes to their Tor Weather preferences.

        @type pref_auth: str
        @param pref_auth: The user's unique preferences authorization key,
            which is used to prevent inappropriate access of this page and to 
            access specific information about the user from the database 
            (pref_auth, unsubs_auth) to be displayed on the page. The key is 
            incorporated into the url.
        @rtype: str
        @return: The url extension for the user-specific preferences changed 
            page.
        """
        extension = path % pref_auth
        return extension

    @staticmethod
    def get_error_ext(error_type, 
                      key,
                      path = __ERROR):
        """Returns the url extension for the error page specified by the 
        error_type 
        parameter.

        @type error_type: str
        @param error_type: The type of error message to be displayed to the 
            user.
        @type key: str
        @param key: A user-specific key, the meaning of which depends on the 
            type of error encountered. For a fingerprint not found error, the
            key represents the fingerprint the user tried to enter. For an 
            already subscribed error, the key is the user's preferences 
            authorization key, which is utilized in page rendering. The key is
            incorporated into the url extension.
        @rtype: str
        @return: The url extension for the user-specific error page.
        """
        extension = path % (error_type, key)
        return extension 

    @staticmethod
    def get_fingerprint_error_ext(fingerprint,
                                  path = __FINGERPRINT_ERROR):
        """Returns the url extension for the page alerting the user that the 
        fingerprint they are trying to monitor doesn't exist in the database.

        @type fingerprint: str
        @param fingerprint: The fingerprint the user entered, which is
            incorporated into the url.
        @rtype: str
        @return: The url extension for the user-specific fingerprint error 
            page. 
        """
        extension = path % fingerprint
        return extension

    @staticmethod
    def get_home_ext(path = __HOME):
        """Returns the url extension for the Tor Weather home page.

        @rtype: str
        @return: The url extension for the Tor Weather home page.
        """
        extension = path
        return extension
    
    @staticmethod
    def get_pending_ext(confirm_auth,
                        path = __PENDING):
        """Returns the url extension for the pending page, displayed when the
        user submits an acceptable subscribe form.

        @type confirm_auth: str
        @param confirm_auth: The user's unique confirmation authorization key,
            which is used to prevent inappropriate access to this page and to
            access information about the user from the database (email, node
            fingerprint). The key is incorporated into the url.
        @rtype: str
        @return: The url extension for the user-specific pending page.
        """
        extension = path % confirm_auth
        return extension

    @staticmethod
    def get_preferences_url(pref_auth,
                            path = __PREFERENCES):
        """Returns the complete url for the preferences page, which is displayed
        to the user in the email reports and on some of the Tor Weather pages.

        @type pref_auth: str
        @param pref_auth: The user's unique preferences authorization key, which
            is incorporated into the url.
        @rtype: str
        @return: The complete url that links to the page allowing the user to 
            change his or her Tor Weather preferences.
        """
        url = base_url + path % pref_auth
        return url

    @staticmethod
    def get_subscribe_ext(path = __SUBSCRIBE):
        """Returns the url extension for the Tor Weather subscribe page. 
        
        @rtype: str
        @return: The url extension for the subscribe page.
        """
        extension = path
        return extension

    @staticmethod
    def get_unsubscribe_url(unsubs_auth,
                            path = __UNSUBSCRIBE):
        """Returns the complete url for the user's unsubscribe page. The url is
        displayed to the user in the email reports and on some of the Tor 
        Weather pages.

        @type unsubs_auth: str
        @param unsubs_auth: The user's unique unsubscribe authorization key, 
            which is incorporated into the url.
        @rtype: str
        @return: The complete url for the user's unique unsubscribe page.
        """
        url = base_url + path % unsubs_auth
        return url
