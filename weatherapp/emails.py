baseURL = http://localhost:8000
_SENDER = 'tor-ops@torproject.org'
_SUBJECT_HEADER = '[Tor Weather] '

_CONFIRMATION_SUBJ = 'Confirmation Needed'
_CONFIRMATION_MAIL = """
Dear human,

This is the Tor Weather Report system.

Somebody (possibly you) has requested that status monitoring information
about a Tor node (id: %s) be sent to this email address.

If you wish to confirm this request, please visit the following url:

%s

If you do not wish to receive Tor Weather Reports, you do not need to do 
anything.
"""

_CONFIRMED_SUBJ = 'Confirmation Successful'
_SUBS_CONFIRMED_MAIL = """
Dear human,

This is the Tor Weather Report system.

You successfully subscribed for weather reports about a tor node.

(node id: %s)

You can unsubscribe from these reports at any time by visiting the 
following url:

%s 

or change your Tor Weather notification preferences here:

%s.
"""

_NODE_DOWN_SUBJ = 'Node Down!'
_NODE_DOWN_MAIL = """
This is a Tor Weather Report.

It appears that a Tor node you elected to monitor, 

(node id: %s),

has been uncontactable through the Tor network for at least %s.  You may wish
to look at it to see why.  

You can unsubscribe from these reports at any time by visiting the
following url:

%s 

or change your Tor Weather notification preferences here:

%s.
"""
# ------------------------------------------------------------------
# CONFIGURE THIS!
# ------------------------------------------------------------------
_OUT_OF_DATE_SUBJ = 'Node Out of Date!'
_OUT_OF_DATE_MAIL = """
This is a Tor Weather Report.

It appears that a Tor node you elected to monitor,

(node id: %s),

is running an out of date version of Tor. You can download the latest 
version of Tor at %s. 

You can unsubscribe from these reports at any time by visiting the
following url: 

%s

or change your Tor Weather notification preferences here:

%s.
"""

_T_SHIRT_SUBJ = 'Congratulations! Have a t-shirt!'
_T_SHIRT_MAIL = """
This is a Tor Weather Report.

Congratulations! The node you are observing has been stable for %s,
which makes the operator eligible to receive an official Tor T-shirt!
If you're interested in claiming your shirt, please visit the following
link for more information. 

http://www.torproject.org/tshirt.html

Thank you for your contribution to the Tor network!

You can unsubscribe from these reports at any time by visiting the
following url:

%s

or change your Tor Weather notification preferences here:

%s.
"""

_WELCOME_SUBJ = 'Welcome to Tor!'
_WELCOME_MAIL = """
Hello and welcome to Tor!

We've noticed that your Tor node has been running long enough to be
flagged as "stable". First, we would like to thank you for your 
contribution to the Tor network! As Tor grows, we require ever more 
nodes to optomize browsing speed and reliability for our users. Your 
node is helping to serve the millions of Tor clients out there.

As a node operator, you may be interested in the Tor Weather service,
which sends important email notifications when a node is down or 
your version is out of date. We here at Tor consider this service to
be vitally important and greatly useful to all node operators. If you're 
interested in Tor Weather, please visit the following link to register:
 
https://weather.torproject.org/

You might also be interested in the or-announce mailing list, which is
a low volume list for announcements of new releases and critical 
security updates. To join, send an e-mail message to majordomo@seul.org
with no subject and a body of "subscribe or-announce". 

Thank you again for your contribution to the Tor network! We won't send
you any further emails unless you subscribe.


Disclaimer: If you have no idea why you're receiving this email, we 
sincerely apologize and promise never to email you again!
"""

_LEGAL_SUBJ = 'Welcome to Tor! Thanks for agreeing to be an exit node!'
_LEGAL_MAIL = """
Legal mumbo jumbo
"""

class Emailer:
    @staticmethod
    def send_confirmation(recipient,
                          conf_auth,
                          sender = _SENDER,
                          subj_header = _SUBJECT_HEADER):
        subj = _SUBJ_HEADER + _CONFIRMATION_SUBJ
        msg = _CONFIRMATION_MAIL % baseURL + '/confirm/' + conf_auth + '/'
        send_mail(subj, msg, sender, [recipient], fail_silently=True)

    @staticmethod
    def send_confirmed(recipient,
                       fingerprint,
                       unsub_auth,
                       pref_auth,
                       sender = _SENDER,
                       subj_header = _SUBJECT_HEADER):
        subj = _SUBJ_HEADER + _CONFIRMED_SUBJ
        unsubURL = baseURL + '/unsubscribe/' + unsub_auth + '/'
        prefURL = baseURL + '/preferences/' + pref_auth + '/'
        msg = _CONFIRMED_MAIL % fingerprint, unsubURL, prefURL 
        send_mail(subj, msg, sender, [recipient], fail_silently=True)

    @staticmethod
    def send_node_down(recipient,
                       fingerprint,
                       grace_pd,
                       unsub_auth,
                       pref_auth,
                       sender = _SENDER,
                       subj_header = _SUBJECT_HEADER):
        subj = _SUBJ_HEADER + _NODE_DOWN_SUBJ
        unsubURL = baseURL + '/unsubscribe/'+ unsub_auth + '/'
        prefURL = baseURL + '/preferences/' + pref_auth + '/'
        msg = _NODE_DOWN_MAIL % fingerprint, grace_pd, unsubURL, prefURL
        send_mail(subj, msg, sender, [recipient], fail_silently=True)

    @staticmethod
    def send_t_shirt(recipient,
                     unsub_auth,
                     pref_auth,
                     sender = _SENDER,
                     subj_header = _SUBJECT_HEADER):
        subj = _SUBJ_HEADER + _T_SHIRT_SUBJ
        unsubURL = baseURL + '/unsubscribe/' + unsub_auth + '/'
        prefURL = baseURL + '/preferences/' + pref_auth + '/'
        msg = _T_SHIRT_MAIL % unsubURL, prefURL
        send_mail(subj, msg, sender, [recipient], fail_silently=True)

    @staticmethod
    def send_welcome(recipient,
                     sender = _SENDER,
                     subj_header = _SUBJECT_HEADER):
        subj = _SUBJ_HEADER + _WELCOME_SUBJ
        msg = _WELCOME_MAIL 
        send_mail(subj, msg, sender, [recipient], fail_silently=True)

    @staticmethod
    def send_legal(recipient,
                   # PUT REQUIRED NUMBER OF % PARAMETERS HERE
                   sender = _SENDER,
                   subj_header = _SUBJECT_HEADER):
        subj = _SUBJ_HEADER + _WELCOME_SUBJ
        msg = _LEGAL_MAIL #% PUT PARAMETERS HERE
        send_mail(subj, msg, sender, [recipient], fail_silently=True)
