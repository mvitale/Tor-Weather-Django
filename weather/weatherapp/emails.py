"""The emails module contains methods to send individual confirmation and confirmed emails as well as methods to return tuples needed by Django's 
send_mass_mail() method. Emails are sent after all database checks/updates. 

@type _SENDER: str
@var _SENDER: The email address for the Tor Weather emailer
@type _SUBJECT_HEADER: str
@var _SUBJECT_HEADER: The base for all email headers.
@type _CONFIRMATION_SUBJ: str
@var _CONFIRMATION_SUBJ: The subject line for the confirmation mail
@type _CONFIRMATION_MAIL: str
@var _CONFIRMATION_MAIL: The email message sent upon first 
    subscribing. The email contains a link to the user-specific confirmation
    page, which the user must follow to confirm.
@type _CONFIRMED_SUBJ: str
@var _CONFIRMED_SUBJ: The subject line for the confirmed email
@type _CONFIRMED_MAIL: str
@var _CONFIRMED_MAIL: The email message sent after the user follows the 
    link in the confirmation email. Contains links to preferences and 
    unsubscribe.
@type _NODE_DOWN_SUBJ: str
@var _NODE_DOWN_SUBJ: The subject line for the node down notification
@type _NODE_DOWN_MAIL: str
@var _NODE_DOWN_MAIL: The email message for the node down notification.
@type _VERSION_SUBJ: str
@var _VERSION_SUBJ: The subject line for an out-of-date version notification
@type _VERSION_MAIL: str
@var _VERSION_MAIL: The email message for an out-of-date version 
    notification
@type _LOW_BANDWIDTH_SUBJ: str
@var _LOW_BANDWIDTH_SUBJ: The subject line for the low bandwidth notification. 
@type _LOW_BANDWIDTH_MAIL: str
@var _LOW_BANDWIDTH_MAIL: The email message for the low bandwidth notification.
@type _T_SHIRT_SUBJ: str
@var _T_SHIRT_SUBJ: The subject line for the T-Shirt notification
@type _T_SHIRT_MAIL: str
@var _T_SHIRT_MAIL: The email message for the T-Shirt notification (includes 
    uptime and avg bandwidth over that period)
@type _WELCOME_SUBJ: str
@var _WELCOME_SUBJ: The subject line for the welcome email
@type _WELCOME_MAIL: str
@var _WELCOME_MAIL: The message in the welcome email. This message is sent to
    all node operators running a stable node (assuming we can parse their 
    email). It welcomes the user to Tor, describes Tor Weather, and provides 
    legal information if the user is running an exit node.
@type _LEGAL_INFO: str
@var _LEGAL_INFO: Legal information to assist exit node operators. This is 
    appended to the welcome email if the recipient runs an exit node.
@type _GENERIC_FOOTER: str
@var _GENERIC_FOOTER: A footer containing unsubscribe and preferences page
    links.
"""
import re

from config import url_helper
from weatherapp.models import insert_fingerprint_spaces

from django.core.mail import send_mail

_SENDER = 'tor-ops@torproject.org'
_SUBJECT_HEADER = '[Tor Weather] '

_CONFIRMATION_SUBJ = 'Confirmation Needed'
_CONFIRMATION_MAIL = "Dear human,\n\n" +\
    "This is the Tor Weather Report system.\n\n" +\
    "Someone (possibly you) has requested that status monitoring "+\
    "information about a Tor node %s be sent to this email "+\
    "address.\n\nIf you wish to confirm this request, please visit the "+\
    "following url:\n\n%s\n\nIf you do not wish to receive Tor Weather "+\
    "Reports, you don't need to do anything. You shouldn't hear from us "+\
    "again."

_CONFIRMED_SUBJ = 'Confirmation Successful'
_CONFIRMED_MAIL="Dear human,\n\nThis is the Tor Weather Report "+\
    "system.You successfully subscribed for Weather Reports about a Tor "+\
    "node %s."

_NODE_DOWN_SUBJ = 'Node Down!'
_NODE_DOWN_MAIL = "This is a Tor Weather Report.\n\n" +\
    "It appears that the node %s you've been observing" +\
    "has been uncontactable through the Tor network for at least %s. "+\
    "You may wish to look at it to see why."

_VERSION_SUBJ = 'Node Out of Date!'
_VERSION_MAIL = "This is a Tor Weather Report.\n\n"+\
    "It appears that the Tor node %s you've been observing "+\
    "is running an %s version of Tor. You can download the "+\
    "latest version of Tor at %s."

_LOW_BANDWIDTH_SUBJ = 'Low bandwidth!'
_LOW_BANDWIDTH_MAIL = "The is a Tor Weather Report.\n\n"+\
    "It appears that the tor node %s you've been observing "+\
    "has an observed bandwidth capacity of %s kB/s. You elected to receive "+\
    "notifications if this node's bandwidth capacity passed a threshold of "+\
    "%s kB/s. You may wish to look at your router to see why."

_T_SHIRT_SUBJ = 'Congratulations! Have a T-shirt!'
_T_SHIRT_MAIL = "This is a Tor Weather Report.\n\n"+\
    "Congratulations! The node %s you've been observing has been %s for %s "+\
    "days with an average bandwidth of %s KB/s," +\
    "which makes the operator eligible to receive an official Tor "+\
    "T-shirt! If you're interested in claiming your shirt, please visit "+\
    "the following link for more information.\n\n"+\
    "https://www.torproject.org/tshirt.html"+\
    "\n\nYou might want to include this message in your email. "+\
    "Thank you for your contribution to the Tor network!"
    
_WELCOME_SUBJ = 'Welcome to Tor!'
_WELCOME_MAIL = "Hello and welcome to Tor!\n\n" +\
    "We've noticed that your Tor node %s has been running long "+\
    "enough to be "+\
    "flagged as \"stable\". First, we would like to thank you for your "+\
    "contribution to the Tor network! As Tor grows, we require ever more "+\
    "nodes to optomize browsing speed and reliability for our users. "+\
    "Your node is helping to serve the millions of Tor clients out there."+\
    "\n\nAs a node operator, you may be interested in the Tor Weather "+\
    "service, which sends important email notifications when a node is "\
    "down or your version is out of date. We here at Tor consider this "+\
    "service to be vitally important and greatly useful to all node "+\
    "operators. If you're interested in Tor Weather, please visit the "+\
    "following link to register:\n\n"+\
    "%s\n\n"+\
    "You might also be interested in the or-announce mailing list, "+\
    "which is a low volume list for announcements of new releases and "+\
    "critical security updates. To join, send an e-mail message to "+\
    "majordomo@seul.org "+\
    "with no subject and a body of \"subscribe or-announce\". \n\n"+\
    "%sThank you again for your contribution to the Tor network! "+\
    "We won't send you any further emails unless you subscribe.\n\n"+\
    "Disclaimer: If you have no idea why you're receiving this email, we "+\
    "sincerely apologize! You shouldn't hear from us again."

_LEGAL_INFO = "Additionally, since you are running as an exit node, you " +\
    "might be interested in Tor's Legal FAQ for Relay Operators "+\
    "(https://www.torproject.org/eff/tor-legal-faq.html.en) " +\
    "and Mike Perry's blog post on running an exit node " +\
    "(https://blog.torproject.org/blog/tips-running-exit-node-minimal-"+\
    "harassment).\n\n"

_GENERIC_FOOTER = "\n\nYou can unsubscribe from these reports at any time "+\
    "by visiting the following url:\n\n%s\n\nor change your Tor Weather "+\
    "notification preferences here: \n\n%s"


def _get_router_name(fingerprint, name):
    """Returns a string representation of the name and fingerprint of
    this router. Ex: 'WesCSTor (id: 4094 8034 ...)'
    
    @type fingerprint: str
    @param fingerprint: A router fingerprint
    @type name: str
    @param name: A router name

    @rtype: str
    @return: An email-friendly string representation of the name and
    fingerprint. Only returns a representation of the fingerprint 
    C{if name == 'Unnamed'}.
    """

    spaced_fingerprint = insert_fingerprint_spaces(fingerprint) 
    if name == 'Unnamed':
        return "(id: %s)" % spaced_fingerprint
    else:
        return "%s (id: %s)" % (name, spaced_fingerprint)

def _add_generic_footer(msg, unsubs_auth, pref_auth):
    """
    Appends C{_GENERIC_FOOTER} to C{msg} with unsubscribe and preferences
    links created from C{unsubs_auth} and C{pref_auth}.

    @type msg: str
    @param msg: The message to append the footer to.
    @type unsubs_auth: str
    @param msg: The user's unique unsubscribe auth key.
    @type pref_auth: str
    @param pref_auth: The user's unique unsubscribe auth key.

    @rtype: str
    @return: C{msg} with the footer appended.
    """

    unsubURL = url_helper.get_unsubscribe_url(unsubs_auth)
    prefURL = url_helper.get_preferences_url(pref_auth)
    footer = _GENERIC_FOOTER % (unsubURL, prefURL)
    
    return msg + footer

def send_confirmation(recipient, fingerprint, name, confirm_auth):
    """This method sends a confirmation email to the user. The email 
    contains a complete link to the confirmation page, which the user 
    must follow in order to subscribe. The Django method send_mail is
    called with fail_silently=True so that an error is not thrown if the
    mail isn't successfully delivered.
    
    @type recipient: str
    @param recipient: The user's email address
    @type fingerprint: str
    @param fingerprint: The fingerprint of the node this user wishes to
        monitor.
    @type confirm_auth: str
    @param confirm_auth: The user's unique confirmation authorization key.
    """
    router = _get_router_name(fingerprint, name)
    confirm_url = url_helper.get_confirm_url(confirm_auth)
    msg = _CONFIRMATION_MAIL % (router, confirm_url)
    sender = _SENDER
    subj = _SUBJECT_HEADER + _CONFIRMATION_SUBJ
    send_mail(subj, msg, sender, [recipient], fail_silently=True)

def send_confirmed(recipient, fingerprint, name, unsubs_auth, pref_auth):
    """Sends an email to the user after their subscription is successfully
    confirmed. The email contains links to change preferences and 
    unsubscribe.
    
    @type recipient: str
    @param recipient: The user's email address
    @type fingerprint: str
    @param fingerprint: The fingerprint of the node this user wishes to
        monitor.
    @type unsubs_auth: str
    @param unsubs_auth: The user's unique unsubscribe auth key
    @type pref_auth: str
    @param pref_auth: The user's unique preferences auth key
    """
    router = _get_router_name(fingerprint, name)
    subj = _SUBJECT_HEADER + _CONFIRMED_SUBJ
    sender = _SENDER
    unsubURL = url_helper.get_unsubscribe_url(unsubs_auth)
    prefURL = url_helper.get_preferences_url(pref_auth)
    msg = _CONFIRMED_MAIL % router
    msg = _add_generic_footer(msg, unsubURL, prefURL)
    send_mail(subj, msg, sender, [recipient], fail_silently=False)

def bandwidth_tuple(recipient, fingerprint, name,  observed, threshold,
                    unsubs_auth, pref_auth):
    """Returns the tuple for a low bandwidth email.
    @type recipient: str
    @param recipient: The user's email address
    @type fingerprint: str
    @param fingerprint: The fingerprint of the node this user wishes to
        monitor.
    @type observed: int
    @param observed: The observed bandwidth (kB/s)
    @type threshold: int
    @param threshold: The user's specified threshold for low bandwidth (KB/s)
    @type unsubs_auth: str
    @param unsubs_auth: The user's unique unsubscribe auth key
    @type pref_auth: str
    @param pref_auth: The user's unique preferences auth key
    """
    router = _get_router_name(fingerprint, name)
    subj = _SUBJECT_HEADER + _LOW_BANDWIDTH_SUBJ
    sender = _SENDER
    unsubURL = url_helper.get_unsubscribe_url(unsubs_auth)
    prefURL = url_helper.get_preferences_url(pref_auth)

    msg = _LOW_BANDWIDTH_MAIL % (router, observed, threshold)
    msg = _add_generic_footer(msg, unsubURL, prefURL)

    return (subj, msg, sender, [recipient])

def node_down_tuple(recipient, fingerprint, name, grace_pd, unsubs_auth, 
                    pref_auth):
    """Returns the tuple for a node down email.
    @type recipient: str
    @param recipient: The user's email address
    @type fingerprint: str
    @param fingerprint: The fingerprint of the node this user wishes to
        monitor.
    @type grace_pd: int
    @param grace_pd: The amount of downtime specified by the user
    @type unsubs_auth: str
    @param unsubs_auth: The user's unique unsubscribe auth key
    @type pref_auth: str
    @param pref_auth: The user's unique preferences auth key
    @rtype: tuple
    @return: A tuple listing information about the email to be sent, which is
        used by the send_mass_mail method in updaters.
    """
    router = _get_router_name(fingerprint, name)
    subj = _SUBJECT_HEADER + _NODE_DOWN_SUBJ
    sender = _SENDER
    num_hours = grace_pd + " hour"
    if grace_pd > 1:
        num_hours += "s"
    unsubURL = url_helper.get_unsubscribe_url(unsubs_auth)
    prefURL = url_helper.get_preferences_url(pref_auth)
    msg = _NODE_DOWN_MAIL % (router, num_hours)
    msg = _add_generic_footer(msg, unsubURL, prefURL)
    return (subj, msg, sender, [recipient])

def t_shirt_tuple(recipient, fingerprint, name, avg_bandwidth, 
                  hours_since_triggered, is_exit, unsubs_auth, pref_auth):
    """Returns a tuple for a t-shirt earned email.  
    @type recipient: str
    @param recipient: The user's email address
    @type fingerprint: str
    @param fingerprint: The router's fingerprint
    @type avg_bandwidth: int
    @param avg_bandwidth: The user's average bandwidth over the
        observed period in kB/s.
    @type hours_since_triggered: int
    @param hours_since_triggered: The hours since the user's router
        was first viewed as running.
    @type is_exit: bool
    @param is_exit: True if the router is an exit node, False if not.
    @type unsubs_auth: str
    @param unsubs_auth: The user's unique unsubscribe auth key
    @type pref_auth: str
    @param pref_auth: The user's unique preferences auth key
    @rtype: tuple
    @return: A tuple listing information about the email to be sent, which is
        used by the send_mass_mail method in updaters.
    """
    router = _get_router_name(fingerprint, name)
    stable_message = 'running'
    if is_exit:
        node_type += ' as an exit node'
    days_running = hours_since_triggered / 24
    avg_bandwidth = avg_bandwidth
    subj = _SUBJECT_HEADER + _T_SHIRT_SUBJ
    sender = _SENDER
    unsubURL = url_helper.get_unsubscribe_url(unsubs_auth)
    prefURL = url_helper.get_preferences_url(pref_auth)
    msg = _T_SHIRT_MAIL % (router, stable_message, days_running, 
                           avg_bandwidth)
    msg = _add_generic_footer(msg, unsubURL, prefURL)
    return (subj, msg, sender, [recipient])

def welcome_tuple(recipient, fingerprint, name, exit):
    """Returns a tuple for the welcome email. If the operator runs an exit
    node, legal information is appended to the welcome mail.

    @type recipient: str
    @param recipient: The user's email address.
    @type fingerprint: str
    @param fingerprint: The fingerprint for the router this user is subscribed
        to.
    @type exit: bool
    @param exit: C{True} if the router is an exit node, C{False} if not.
    @rtype: tuple
    @return: A tuple listing information about the email to be sent, which is
        used by the send_mass_mail method in updaters.
    """
    router = _get_router_name(fingerprint, name)
    subj = _SUBJECT_HEADER + _WELCOME_SUBJ
    sender = _SENDER
    append = ''
    # if the router is an exit node, append legal info 
    if exit:
        append = _LEGAL_INFO
    url = url_helper.get_home_url()
    msg = _WELCOME_MAIL % (router, url, append)
    return (subj, msg, sender, [recipient])

def version_tuple(recipient, fingerprint, name, version_type, unsubs_auth, 
                  pref_auth):
    """Returns a tuple for a version notification email.

    @type recipient: str
    @param recipient: The user's email address.
    @type fingerprint: str
    @param fingerprint: The fingerprint for the router this user is subscribed
                        to.
    @type version_type: str
    @param version_type: Either 'UNRECOMMENDED' or 'OBSOLETE', depending on the
        user's preferences for this notification type.

    @rtype: tuple
    @return: A tuple containing information about the email to be sent in
             an appropriate format for the C{send_mass_mail()} function in
             C{updaters}.
    """
    router = _get_router_name(fingerprint, name)
    subj = _SUBJECT_HEADER + _VERSION_SUBJ
    sender = _SENDER
    version_type = version_type.lower()
    unsubURL = url_helper.get_unsubscribe_url(unsubs_auth)
    prefURL = url_helper.get_preferences_url(pref_auth)
    downloadURL = url_helper.get_download_url()
    msg = _VERSION_MAIL % (router, version_type, downloadURL)
    msg = _add_generic_footer(msg, unsubURL, prefURL)
                           
    return (subj, msg, sender, [recipient])
