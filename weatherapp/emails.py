from django.core.mail import send_mail
from weather.config.web_directory import Urls

_SENDER = 'tor-ops@torproject.org'
_SUBJECT_HEADER = '[Tor Weather] '

_CONFIRMATION_SUBJ = 'Confirmation Needed'
_CONFIRMATION_MAIL = "Dear human,\n\n" +\
"This is the Tor Weather Report system.\n\n" +\
"Someone (possibly you) has requested that status monitoring information "+\
"about a Tor node (id: %s) be sent to this email address.\n\n" +\
"If you wish to confirm this request, please visit the following url:\n\n" +\
"%s\n\n" +\
"If you do not wish to receive Tor Weather Reports, you don't need to do " +\
"anything. You shouldn't hear from us again.\n"

_CONFIRMED_SUBJ = 'Confirmation Successful'
_SUBS_CONFIRMED_MAIL ="Dear human,\n\nThis is the Tor Weather Report system."+\
"You successfully subscribed for Weather Reports about a Tor node.\n\n"+\
"(node id: %s)\n\n" +\
"You can unsubscribe from these reports at any time by visiting the "+\
"following url:\n\n%s\n\n or change your Tor Weather notification " +\
"preferences here: \n\n%s.\n"

_NODE_DOWN_SUBJ = 'Node Down!'
_NODE_DOWN_MAIL = "This is a Tor Weather Report.\n\n" +\
"It appears that a Tor node you elected to monitor (node id: %s) " +\
"has been uncontactable through the Tor network for at least %s hour(s). "+\
"You may wish to look at it to see why.\n\n You can unsubscribe from these "+\
"reports at any time by visiting the following url:\n\n%s\n\n or change your "+\
"Tor Weather notification preferences here:\n\n%s.\n"
# ------------------------------------------------------------------
# CONFIGURE THIS!
# ------------------------------------------------------------------
_OUT_OF_DATE_SUBJ = 'Node Out of Date!'
_OUT_OF_DATE_MAIL = "This is a Tor Weather Report.\n\n"+\
"It appears that a Tor node you elected to monitor (node id: %s) "+\
"is running an out of date version of Tor. You can download the latest "+\
"version of Tor at %s.\n\n You can unsubscribe from these reports at any "+\
"time by visiting the following url:\n\n%s\n\nor change your Tor Weather "+\
"notification preferences here:\n\n%s.\n"

_T_SHIRT_SUBJ = 'Congratulations! Have a t-shirt!'
_T_SHIRT_MAIL = "This is a Tor Weather Report.\n\n"+\
"Congratulations! The node you are observing has been stable for %s, "+\
"which makes the operator eligible to receive an official Tor T-shirt! "+\
"If you're interested in claiming your shirt, please visit the following "+\
"link for more information.\n\n"+\
"http://www.torproject.org/tshirt.html"+\
"Thank you for your contribution to the Tor network!"+\
"You can unsubscribe from these reports at any time by visiting the "+\
"following url:\n\n%s\n\nor change your Tor Weather notification "+\
"preferences here:\n\n%s\n"


_WELCOME_SUBJ = 'Welcome to Tor!'
_WELCOME_MAIL = "Hello and welcome to Tor!\n\n" +\
"We've noticed that your Tor node has been running long enough to be "+\
"flagged as \"stable\". First, we would like to thank you for your "+\
"contribution to the Tor network! As Tor grows, we require ever more "+\
"nodes to optomize browsing speed and reliability for our users. Your "+\
"node is helping to serve the millions of Tor clients out there.\n\n" +\
"As a node operator, you may be interested in the Tor Weather service, "+\
"which sends important email notifications when a node is down or "+\
"your version is out of date. We here at Tor consider this service to "+\
"be vitally important and greatly useful to all node operators. If you're "+\
"interested in Tor Weather, please visit the following link to register:\n\n"+\
"https://weather.torproject.org/\n\n"+\
"You might also be interested in the or-announce mailing list, which is "+\
"a low volume list for announcements of new releases and critical "+\
"security updates. To join, send an e-mail message to majordomo@seul.org "+\
"with no subject and a body of \"subscribe or-announce\". \n\n"+\
"Thank you again for your contribution to the Tor network! We won't send "+\
"you any further emails unless you subscribe.\n\n"+\
"Disclaimer: If you have no idea why you're receiving this email, we "+\
"sincerely apologize! You shouldn't hear from us again.\n"

_LEGAL_SUBJ = 'Welcome to Tor! Thanks for agreeing to be an exit node!'
_LEGAL_MAIL = """
Legal mumbo jumbo
"""

class Emailer:
    """The Emailer class contains methods to send Weather Report emails to Tor 
    Weather users."""

    @staticmethod
    def send_confirmation(recipient,
                          fingerprint,
                          confirm_auth,
                          sender = _SENDER,
                          subj_header = _SUBJECT_HEADER):
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
        @type sender: str
        @param sender: The sender's email address. Default = the stored 
            email address for the Tor Weather Notification System.
        @type subj_header: str
        @param subj_header: The subj
        """
        subj = subj_header + _CONFIRMATION_SUBJ
        confirm_url = Urls.get_confirm_url(confirm_auth)
        msg = _CONFIRMATION_MAIL % (fingerprint, confirm_url)
        send_mail(subj, msg, sender, [recipient], fail_silently=True)

    @staticmethod
    def send_confirmed(recipient,
                       fingerprint,
                       unsubs_auth,
                       pref_auth,
                       sender = _SENDER,
                       subj_header = _SUBJECT_HEADER):
        """"""
        subj = subj_header + _CONFIRMED_SUBJ
        unsubURL = Urls.get_unsubscribe_url(unsubs_auth)
        prefURL = Urls.get_preferences_url(pref_auth)
        msg = _CONFIRMED_MAIL % (fingerprint, unsubURL, prefURL) 
        send_mail(subj, msg, sender, [recipient], fail_silently=True)

    @staticmethod
    def send_node_down(recipient,
                       fingerprint,
                       grace_pd,
                       unsubs_auth,
                       pref_auth,
                       sender = _SENDER,
                       subj_header = _SUBJECT_HEADER):
        """"""
        subj = subj_header + _NODE_DOWN_SUBJ
        unsubURL = Urls.get_unsubscribe_url(unsubs_auth)
        prefURL = Urls.get_preferences_url(pref_auth)
        msg = _NODE_DOWN_MAIL % (fingerprint, grace_pd, unsubURL, prefURL)
        send_mail(subj, msg, sender, [recipient], fail_silently=True)

    @staticmethod
    def send_t_shirt(recipient,
                     unsubs_auth,
                     pref_auth,
                     sender = _SENDER,
                     subj_header = _SUBJECT_HEADER):
        """"""
        subj = subj_header + _T_SHIRT_SUBJ
        unsubURL = Urls.get_unsubscribe_url(unsubs_auth)
        prefURL = Urls.get_preferences_url(pref_auth)
        msg = _T_SHIRT_MAIL % (unsubURL, prefURL)
        send_mail(subj, msg, sender, [recipient], fail_silently=True)

    @staticmethod
    def send_welcome(recipient,
                     sender = _SENDER,
                     subj_header = _SUBJECT_HEADER):
        """"""
        subj = subj_header + _WELCOME_SUBJ
        msg = _WELCOME_MAIL 
        send_mail(subj, msg, sender, [recipient], fail_silently=True)

    @staticmethod
    def send_legal(recipient,
                   # PUT REQUIRED NUMBER OF % PARAMETERS HERE
                   sender = _SENDER,
                   subj_header = _SUBJECT_HEADER):
        """"""
        subj = subj_header + _WELCOME_SUBJ
        msg = _LEGAL_MAIL #% PUT PARAMETERS HERE
        send_mail(subj, msg, sender, [recipient], fail_silently=True)
