"""The url_helper module stores all of the url extensions and methods for 
accessing them. That way, all of the url extensions can be changed in one 
place if they are ever modified in urls.py.

@var base_url: The base URL for the Tor Weather web application.
@var _CONFIRM: The url pattern for the confirmation page.
@var _CONFIRM_PREF: The url pattern for the preferences confirmed page.
@var _ERROR: The url pattern for the error page.
@var _FINGERPRINT_NOT_FOUND: The url pattern for the fingerprint not found page.
@var _HOME: The url pattern for the Tor Weather home page.
@var _PENDING: The url pattern for the pending page.
@var _PREFERENCES: The url pattern for the change preferences page.
@var _RESEND_CONF: The url pattern for the page displayed after the confirmation
    needed email is resent.
@var _SUBSCRIBE: The url pattern for the subscribe form page.
@var _UNSUBSCRIBE: The url pattern for the page displayed when the user 
    unsubscribes.
@var _DOWNLOAD: The url for the Tor download page.
@var _T_SHIRT: The url for the Tor T-Shirt page.
"""
import config 

base_url = config.base_url

_CONFIRM = '/confirm/%s/'
_CONFIRM_PREF = '/confirm_pref/%s/'
_ERROR = '/error/%s/%s/'
_FINGERPRINT_NOT_FOUND = '/fingerprint_not_found/%s/'
_HOME = '/'
_PENDING = '/pending/%s/'
_PREFERENCES = '/preferences/%s/'
_RESEND_CONF = '/resend_conf/%s/'
_SUBSCRIBE = '/subscribe/'
_UNSUBSCRIBE = '/unsubscribe/%s/'
_DOWNLOAD = 'https://www.torproject.org/easy-download.html'
_T_SHIRT = 'https://www.torproject.org/tshirt.html.en'

def get_confirm_url(confirm_auth):
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
    url = base_url + _CONFIRM % confirm_auth
    return url

def get_confirm_pref_ext(pref_auth):
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
    extension = _CONFIRM_PREF % pref_auth
    return extension

def get_error_ext(error_type, key):
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
    extension = _ERROR % (error_type, key)
    return extension 

def get_fingerprint_info_ext(fingerprint):
    """Returns the url extension for the page alerting the user that the 
    fingerprint they are trying to monitor doesn't exist in the database.

    @type fingerprint: str
    @param fingerprint: The fingerprint the user entered, which is
        incorporated into the url.
    @rtype: str
    @return: The url extension for the user-specific fingerprint error 
        page. 
    """
    extension = _FINGERPRINT_NOT_FOUND % fingerprint
    return extension

def get_home_ext():
    """Returns the url extension for the Tor Weather home page.

    @rtype: str
    @return: The url extension for the Tor Weather home page.
    """
    extension = _HOME
    return extension

def get_home_url():
    """Returns the complete url for the Tor Weather home page.

    @rtype: str
    @return: The url extension for the Tor Weather home page.
    """
    url = base_url + _HOME
    return url

def get_pending_ext(confirm_auth):
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
    extension = _PENDING % confirm_auth
    return extension

def get_preferences_url(pref_auth):
    """Returns the complete url for the preferences page, which is displayed
    to the user in the email reports and on some of the Tor Weather pages.

    @type pref_auth: str
    @param pref_auth: The user's unique preferences authorization key, which
        is incorporated into the url.
    @rtype: str
    @return: The complete url that links to the page allowing the user to 
        change his or her Tor Weather preferences.
    """
    url = base_url + _PREFERENCES % pref_auth
    return url

def get_preferences_ext(pref_auth):
    """Returns the url extension for the user-specific preferences page.
    
    @type pref_auth: str
    @param pref_auth: The user's unique preferences authorization key, which
        is incorporated into the url.
    @rtype: str
    @return: The url extension for the user's preferences page.
    """
    ext = _PREFERENCES % pref_auth
    return ext

def get_resend_ext(confirm_auth):
    """Returns the url extension for the page displayed after the user
    asks to be resent their confirmation email.
    
    @type confirm_auth: str
    @param confirm_auth: The user's unique confirmation authorization key,
        which is incorporated into the url extension.
    @rtype: str
    @return: The url extension for the resend confirmation page.
    """
    extension = _RESEND_CONF % confirm_auth
    return extension

def get_subscribe_ext():
    """Returns the url extension for the Tor Weather subscribe page. 
    
    @rtype: str
    @return: The url extension for the subscribe page.
    """
    extension = _SUBSCRIBE
    return extension

def get_unsubscribe_url(unsubs_auth):
    """Returns the complete url for the user's unsubscribe page. The url is
    displayed to the user in the email reports and on some of the Tor 
    Weather pages.

    @type unsubs_auth: str
    @param unsubs_auth: The user's unique unsubscribe authorization key, 
        which is incorporated into the url.
    @rtype: str
    @return: The complete url for the user's unique unsubscribe page.
    """
    url = base_url + _UNSUBSCRIBE % unsubs_auth
    return url

def get_download_url():
    """Returns the Tor downloads urls
    
    @rtype: str
    @return: The url for the Tor downloads page.
    """
    return _DOWNLOAD

def get_t_shirt_url():
    """Returns the Tor t-shirt url

    @rtype: str
    @return: The url for the Tor t-shirt page.
    """
    return _T_SHIRT
