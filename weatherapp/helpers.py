from django.core.mail import send_mail
import emails
import os
import base64

class Emailer:
    """
    A class for sending email messages.

    @ivar sender: Sender for emails sent by this Emailer object. 
                  Default value of 'tor-ops@torproject.org'.
    @type sender: str
    @ivar subj_header: Prefix for subjects sent by this Emailer object.
                       Default value of '[Tor Weather]'.
    @type subj_header: str
    @ivar message_types: Dictionary mapping a name for a message type to a
                         tuple of the form (subject_text, message_text).
                         Default dictionary contains 'confirmation',
                         'confirmed', 'node_down', 'out_of_date', 't_shirt',
                         'welcome', 'welcome_legal'.
    @type message_types: dict[str:str]
   """
    
    __DEFAULT_SENDER = 'tor-ops@torproject.org'
    __DEFAULT_SUBJ_HEADER = '[Tor Weather]'
    __MESSAGE_TYPES = { 'confirmation' : ('Confirmation Needed', 
                                          emails.CONFIRMATION_MAIL),
                        'confirmed'    : ('Confirmation Successful',
                                          emails.SUBS_CONFIRMED_MAIL),
                        'node_down'    : ('Node Down!',
                                          emails.NODE_DOWN_MAIL),
                        'out_of_date'  : ('Node Out of Date!',
                                          emails.OUT_OF_DATE_MAIL),
                        't_shirt'      : ('Congratulations! Have a t-shirt!',
                                          emails.T_SHIRT_MAIL),
                        'welcome'      : ('Welcome to Tor!',
                                          emails.WELCOME_MAIL),
                        'welcome_legal' : ('Welcome to Tor! Thanks for \
                                            Agreeing to Be an Exit Node!',
                                           emails.LEGAL_MAIL), }

    def __init__(self, 
                 sender = __DEFAULT_SENDER, 
                 subj_header = __DEFAULT_SUBJ_HEADER,
                 message_types = __MESSAGE_TYPES):
        self.sender = sender
        self.subj_header = subj_header
        self.message_types = message_types
    
    def send_single_email(self, recipient, message_type,
                          subj_header = "",
                          subject = "",
                          message_text = "",
                          sender = ""):
        """
        Send an email to a single recipient recipient of type message_type

        @param recipient: Recipient of email.
        @type recipient: str
        @param message_type: Type of message to be sent. Valid values are
                             specified by self.message_types.
        @type message_type: str
        @param subj_header: Prefix of subject. If not provided, or specified
                            as the empty string, then is inherited from
                            self.subj_header.
        @type subj_header: str
        @param subject: Subject text of email. If not provided, or specified as
                        the empty string, then is inherited from message_type
                        and self.message_types.
        @type subject: str
        @param message_text: Body text of email. If not provided, or specified
                             as the empty string, then is inherited from 
                             messsage_type and self.message_types.
        @type message_text: str
        @param sender: Sender of email. If not provided, or specified as the 
                       empty string, then is inherited from self.sender.
        @type sender: str
        """
        
        if subj_header == "":
            subj_header = self.subj_header
        if subject == "":
            subject = subj_header + self.message_types[message_type][0]
        if message_text == "":
            message_text = self.message_types[message_type][1]
        if sender == "":
            sender = self.sender

        send_mail(subject, message_text, sender, [recipient],
                  fail_silently=True)
            
    def send_mult_email(self, recipient_list, message_type,
                        subj_header = "",
                        subject = "",
                        message_text = "",
                        sender = ""):
        """
        Send an email to a list of recipients of type message_type

        @param recipient_list: Recipients of email.
        @type recipient_list: list[str]
        @param message_type: Type of message to be sent. Valid values are
                             specified by self.message_types.
        @type message_type: str
        @param subj_header: Prefix of subject. If not provided, or specified
                            as the empty string, then is inherited from
                            self.subj_header.
        @type subj_header: str
        @param subject: Subject text of email. If not provided, or specified as
                        the empty string, then is inherited from message_type
                        and self.message_types.
        @type subject: str
        @param message_text: Body text of email. If not provided, or specified
                             as the empty string, then is inherited from 
                             messsage_type and self.message_types.
        @type message_text: str
        @param sender: Sender of email. If not provided, or specified as the 
                       empty string, then is inherited from self.sender.
        @type sender: str
        """
        if subj_header == "":
            subj_header = self.subj_header
        if subject == "":
            subject = subj_header + self.message_types[message_type][0]
        if message_text == "":
            message_text = self.message_types[message_type][1]
        if sender == "":
            sender = self.sender

        send_mail(subject, message_text, sender, recipient_list,
                  fail_silently=True)


class StringGenerator:
    """A class for generating random strings for use as authorization codes"""
    
    __DEFAULT_LENGTH = 24

    def __init__(self, length = __DEFAULT_LENGTH)
        self.length = length

    def get_rand_string():
        cut_off = length - 24
        if cut_off == 0:
            cut_off = 24

        r = base64.urlsafe_b64encode(os.urandom(18))[:cut_off]

        # some email clients don't like URLs ending in -
        if r.endswith("-"):
            r = r.replace("-", "x")
        return r


