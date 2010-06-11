from django.db import models
from django.core.mail import send_mail
import datetime
import TorCtl.TorCtl
import socket
#import weather.config

class Router(models.Model):
    fingerprint = models.CharField(max_length=200)
    name = models.CharField(max_length=100)
    welcomed = models.BooleanField()
    last_seen = models.DateTimeField('date last seen')
    
    def __unicode__(self):
        return self.fingerprint

class Subscriber(models.Model):
    email = models.EmailField(max_length=75)
    router = models.ForeignKey(Router)
    confirmed = models.BooleanField()

    #change this when more is known?
    confirm_auth = models.CharField(max_length=250) 
    unsubs_auth = models.CharField(max_length=250)
    pref_auth = models.CharField(max_length=250)

    sub_date = models.DateField()

    def __unicode__(self):
        return self.email

class SubscribeForm(forms.Form):
    email = forms.EmailField(max_length=75)
    router_id = forms.CharField(max_length=200)
    grace_pd = forms.IntegerField(default=1)

class Subscription(models.Model):
    subscriber = models.ForeignKey(Subscriber)
    name = models.CharField(max_length=200)
    threshold = models.CharField(max_length=200)
    grace_pd = models.IntegerField()
    emailed = models.BooleanField()
    triggered = models.BooleanField()
    last_changed = models.DateTimeField('date of last change')

    def __unicode__(self):
        return self.name

#class Emailer(models.Model):
#    """A class for sending email messages"""
#    def sendEmail(sender, recipient, messageText, subject):
#        """
#        Send an email with message messageText and subject subject to
#        recipient from sender
#        
#        @type sender: string
#        @param sender: The sender of this email.
#        @type recipient: string
#        @param recipient: The recipient of this email.
#        @type messageText: string
#        @param messageText: The contents of this email.
#        @type subject: string
#        @param subject: The subject of this email.
#        """
#        to = [recipient] #send_mail takes a list of recipients
#        send_mail(subject, messageText, sender, recipient, fail_silently=True)

class TorPing:
    "Check to see if various tor nodes respond to SSL hanshakes"
    def __init__(self, control_host = "127.0.0.1", control_port = 9051):
        self.debugfile = open("debug", "w")

        "Keep the connection to the control port lying around"
        self.control_host = control_host
        self.control_port = control_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((control_host,control_port))
        except:
            errormsg = "Could not connect to Tor control port" + \
                       "Is Tor running on %s with its control port opened on %s?" \
                        % (control_host, control_port)
            logging.error(errormsg)
            print >> sys.stderr, errormsg
            raise
        self.control = TorCtl.Connection(self.sock)
        self.control.authenticate(weather.config.authenticator)
        self.control.debug(self.debugfile)

    def __del__(self):
        self.sock.close()
        del self.sock
        self.sock = None                # prevents double deletion exceptions

        # it would be better to fix TorCtl!
        try:
            self.control.close()
        except:
            logging.error("Exception while closing TorCtl")
            pass

        del self.control
        self.control = None

    def ping(self, nodeId):
        "Let's see if this tor node is up by only asking Tor."
        try:
            info = self.control.get_info(str("ns/id/" + nodeId))
        except TorCtl.ErrorReply, e:
            # If we're getting here, we're likely seeing:
            # ErrorReply: 552 Unrecognized key "ns/id/46D9..."
            # This means that the node isn't recognized by 
            logging.error("ErrorReply: %s" % str(e))
            return False

        except:
            logging.error("Unknown exception in ping()")
            return False

        # If we're here, we were able to fetch information about the router
        return True
