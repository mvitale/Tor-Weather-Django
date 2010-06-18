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
    stored in the templates directory, to instance variables. The templates
    are accessed through specific render methods, which are used by the 
    controllers (see views.py).

    @ivar confirm: The confirmation template, confirm.html. The confirmation 
        page takes
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

class URLs:
    """The URLs class maps all of the url extensions to instance variables
    for easier access by the controllers.

    @ivar
    """

    
