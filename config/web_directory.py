"""
This module contains the constants for urls and html templates as well as
the methods for accessing them. The purpose of putting them all in a 
directory was for convenience of development. If the templates should ever
be renamed, or if the url structure is ever changed, it need only be 
updated in one place (here). 
"""

# -----------------------------------------------------------------------
# DO MORE DOCUMENTATION, ADD URLS CLASS
# -----------------------------------------------------------------------

class Templates:
    """ The Templates class maps all of the html template files, which are
    stored in the templates directory, to instance variables for easier access by
    the controllers (see views.py).

    @ivar confirm: The template for the confirmation page. 
    @ivar confirm_pref: The template to confirm preferences have been changed.
    @ivar error: The generic error template.
    @ivar fingerprint_error: The template for the page displayed when a fingerprint isn't
        found.
    @ivar home: The template for the Tor Weather home page.
    @ivar pending: The template for the pending page displayed after the user submits 
        a subscription form.
    @ivar preferences: The template for the page displaying the form to change preferences.
    @ivar subscribe: The template for the page displaying the subscribe form.
    @ivar unsubscribe: The template for the page displayed when the user unsubscribes
        from Tor Weather.
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
    """The URLs class contains methods for accessing the Tor Weather urls and url 
    extensions.
    """

    #__CONFIRM = 
    #__CONFIRM_PREF =
    #__ERROR =
    #__FINGERPRINT_ERROR =
    #__HOME =
    #__PENDING = 
    #__SUBSCRIBE = 
    #__UNSUBSCRIBE = 

    #def get_confirm_url(
