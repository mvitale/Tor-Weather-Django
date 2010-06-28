from django.core.mail import send_mail
from weather.config.web_directory import Urls

class Emailer:
    """The Emailer class contains methods to send Weather Report emails to Tor 
    Weather users."""

    _SENDER = 'tor-ops@torproject.org'
    _SUBJECT_HEADER = '[Tor Weather] '

    _CONFIRMATION_SUBJ = 'Confirmation Needed'
    _CONFIRMATION_MAIL = "Dear human,\n\n" +\
        "This is the Tor Weather Report system.\n\n" +\
        "Someone (possibly you) has requested that status monitoring "+\
        " information about a Tor node (id: %s) be sent to this email "+\
        "address.\n\nIf you wish to confirm this request, please visit the "+\
        "following url:\n\n%s\n\nIf you do not wish to receive Tor Weather "+\
        "Reports, you don't need to do anything. You shouldn't hear from us "+\
        "again.\n"

    _CONFIRMED_SUBJ = 'Confirmation Successful'
    _CONFIRMED_MAIL="Dear human,\n\nThis is the Tor Weather Report "+\
        "system.You successfully subscribed for Weather Reports about a Tor "+\
        "node (id: %s)\n\nYou can unsubscribe from these reports at any time "+\
        "by visiting the following url:\n\n%s\n\n or change your Tor Weather "+\
        "notification preferences here: \n\n%s\n"

    _NODE_DOWN_SUBJ = 'Node Down!'
    _NODE_DOWN_MAIL = "This is a Tor Weather Report.\n\n" +\
        "It appears that a Tor node you elected to monitor (node id: %s) " +\
        "has been uncontactable through the Tor network for at least %s "+\
        "hour(s). You may wish to look at it to see why.\n\n You can "+\
        "unsubscribe from these reports at any time by visiting the "+\
        "following url:\n\n%s\n\n or change your Tor Weather notification "+\
        "preferences here:\n\n%s\n"
# ------------------------------------------------------------------
# CONFIGURE THIS!
# ------------------------------------------------------------------
    _OUT_OF_DATE_SUBJ = 'Node Out of Date!'
    _OUT_OF_DATE_MAIL = "This is a Tor Weather Report.\n\n"+\
        "It appears that a Tor node you elected to monitor (node id: %s) "+\
        "is running an out of date version of Tor. You can download the "+\
        "latest version of Tor at %s.\n\n You can unsubscribe from these "+\
        "reports at any time by visiting the following url:\n\n%s\n\n"+\
        "or change your Tor Weather notification preferences here:\n\n%s\n"

    _T_SHIRT_SUBJ = 'Congratulations! Have a T-shirt!'
    _T_SHIRT_MAIL = "This is a Tor Weather Report.\n\n"+\
        "Congratulations! The node you are observing has been %s for %s "+\
        "days with an average bandwidth of %s KB/s," +\
        "which makes the operator eligible to receive an official Tor "+\
        "T-shirt! If you're interested in claiming your shirt, please visit "+\
        "the following link for more information.\n\n"+\
        "http://www.torproject.org/tshirt.html"+\
        "\n\nYou might want to include this message in your email. "+\
        "\n\nThank you for your contribution to the Tor network!"+\
        "You can unsubscribe from these reports at any time by visiting the "+\
        "following url:\n\n%s\n\nor change your Tor Weather notification "+\
        "preferences here:\n\n%s\n"


    _WELCOME_SUBJ = 'Welcome to Tor!'
    _WELCOME_MAIL = "Hello and welcome to Tor!\n\n" +\
        "We've noticed that your Tor node has been running long enough to be "+\
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
        "https://weather.torproject.org/\n\n"+\
        "You might also be interested in the or-announce mailing list, "+\
        "which is a low volume list for announcements of new releases and "+\
        "critical security updates. To join, send an e-mail message to "+\
        "majordomo@seul.org "+\
        "with no subject and a body of \"subscribe or-announce\". \n\n"+\
        "Thank you again for your contribution to the Tor network! "+\
        "We won't send you any further emails unless you subscribe.\n\n"+\
        "Disclaimer: If you have no idea why you're receiving this email, we "+\
        "sincerely apologize! You shouldn't hear from us again.\n"

# ------------ FORMAT LINK IN WELCOME MAIL --------------------------

    _LEGAL_SUBJ = 'Welcome to Tor! Thanks for agreeing to be an exit node!'
    _LEGAL_MAIL = """
        Legal mumbo jumbo
        """

    @staticmethod
    def send_confirmation(recipient,
                          fingerprint,
                          confirm_auth):
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
        """
        confirm_url = Urls.get_confirm_url(confirm_auth)
        msg = Emailer._CONFIRMATION_MAIL % (fingerprint, confirm_url)
        sender = Emailer._SENDER
        subj = Emailer._SUBJECT_HEADER + Emailer._CONFIRMATION_SUBJ
        send_mail(subj, msg, sender, [recipient], fail_silently=False)

    @staticmethod
    def send_confirmed(recipient,
                       fingerprint,
                       unsubs_auth,
                       pref_auth):
        """Sends an email to the user after their subscription is successfully
        confirmed. The email contains links to change preferences and 
        unsubscribe.
        
        @type recipient: str
        @param recipient: The user's email address
        @type fingerprint: str
        @param fingerprint: The fingerprint of the node this user wishes to
            monitor.
        @type unsub_auth: str
        @param unsub_auth: The user's unique unsubscribe auth key
        @type pref_auth: str
        @param pref_auth: The user's unique preferences auth key
        """
        subj = Emailer._SUBJECT_HEADER + Emailer._CONFIRMED_SUBJ
        sender = Emailer._SENDER
        unsubURL = Urls.get_unsubscribe_url(unsubs_auth)
        prefURL = Urls.get_preferences_url(pref_auth)
        msg = Emailer._CONFIRMED_MAIL % (fingerprint, unsubURL, prefURL) 
        send_mail(subj, msg, sender, [recipient], fail_silently=False)

    @staticmethod
    def send_node_down(recipient,
                       fingerprint,
                       grace_pd,
                       unsubs_auth,
                       pref_auth):
        """Sends an email to the user about their node being down.
        
        @type recipient: str
        @param recipient: The user's email address
        @type fingerprint: str
        @param fingerprint: The fingerprint of the node this user wishes to
            monitor.
        @type grace_pd: int
        @param grace_pd: The amount of downtime specified by the user
        @type unsub_auth: str
        @param unsub_auth: The user's unique unsubscribe auth key
        @type pref_auth: str
        @param pref_auth: The user's unique preferences auth key
        """
        subj = Emailer._SUBJECT_HEADER + Emailer._NODE_DOWN_SUBJ
        sender = Emailer._SENDER
        unsubURL = Urls.get_unsubscribe_url(unsubs_auth)
        prefURL = Urls.get_preferences_url(pref_auth)
        msg = Emailer._NODE_DOWN_MAIL % (fingerprint, grace_pd, unsubURL,   
                                         prefURL)
        send_mail(subj, msg, sender, [recipient], fail_silently=True)

    @staticmethod
    def send_t_shirt(recipient,
                     avg_bandwidth,
                     hours_since_triggered,
                     is_exit,
                     unsubs_auth,
                     pref_auth):
        """Sends an email to the user notifying them that their node has
        earned them a T-shirt.
        
        @type recipient: str
        @param recipient: The user's email address
        @type avg_bandwidth: int
        @param avg_bandwidth: The user's average bandwidth over the
            observed period.
        @type hours_since_triggered: int
        @param hours_since_triggered: The hours since the user's router
            was first viewed as running.
        @type is_exit: bool
        @param is_exit: True if the router is an exit node, False if not.
        @param unsub_auth: The user's unique unsubscribe auth key
        @type pref_auth: str
        @param pref_auth: The user's unique preferences auth key
        """
        stable_message = 'running'
        if is_exit:
            node_type += ' as an exit node'
        days_running = hours_since_triggered / 24
        avg_bandwidth = avg_bandwidth / 1000
        subj = Emailer._SUBJECT_HEADER + Emailer._T_SHIRT_SUBJ
        sender = Emailer._SENDER
        unsubURL = Urls.get_unsubscribe_url(unsubs_auth)
        prefURL = Urls.get_preferences_url(pref_auth)
        msg = Emailer._T_SHIRT_MAIL % (stable_message, days_running, 
                                       avg_bandwidth, unsubURL, prefURL)
        send_mail(subj, msg, sender, [recipient], fail_silently=True)

    @staticmethod
    def send_welcome(recipient):
        """Sends a welcome email to a stable node operator. The email 
        alerts the operator about Tor Weather and the or-announce mailing 
        list.

        @type recipient: str
        @param recipient: The user's email address.
        """
        subj = Emailer._SUBJECT_HEADER + Emailer._WELCOME_SUBJ
        sender = Emailer._SENDER
        msg = Emailer._WELCOME_MAIL
        send_mail(subj, msg, sender, [recipient], fail_silently=True)

    @staticmethod
    def send_legal(recipient):
                   # PUT REQUIRED NUMBER OF % PARAMETERS HERE
        """"""
        subj = Emailer._SUBJECT_HEADER + Emailer._WELCOME_SUBJ
        sender = Emailer._SENDER
        msg = Emailer._LEGAL_MAIL #% PUT PARAMETERS HERE
        send_mail(subj, msg, sender, [recipient], fail_silently=True)
