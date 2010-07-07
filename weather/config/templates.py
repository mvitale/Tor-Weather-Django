"""The templates module maps all of the html template files, which are
stored in the templates directory, to instance variables for easier access 
by the controllers (see views.py).

@type confirm: str
@var confirm: The template for the confirmation page. 
@type confirm_pref: str
@var confirm_pref: The template to confirm preferences have been changed.
@type error: str
@var error: The generic error template.
@type fingerprint_not_found: str
@var fingerprint_not_found: The template for the page displayed when a 
    fingerprint isn't found.
@type home: str
@var home: The template for the Tor Weather home page.
@type notification_info: str
@var notification_info: The template for the page with notification 
    specifications.
@type pending: str
@var pending: The template for the pending page displayed after the user 
    submits a subscription form.
@type preferences: str
@var preferences: The template for the page displaying the form to change 
    preferences.
@type resend_conf: str
@var resend_conf: The template for the page displayed after the
    confirmation email is resent upon user request.
@type subscribe: str
@var subscribe: The template for the page displaying the subscribe form.
@type unsubscribe: str
@var unsubscribe: The template for the page displayed when the user 
    unsubscribes from Tor Weather.
"""
confirm = 'confirm.html'
confirm_pref = 'confirm_pref.html'
error = 'error.html'
fingerprint_not_found = 'fingerprint_not_found.html'
home = 'home.html'
notification_info = 'notification_info.html'
pending = 'pending.html'
preferences = 'preferences.html'
resend_conf = 'resend_conf.html'
subscribe = 'subscribe.html'
unsubscribe = 'unsubscribe.html'
