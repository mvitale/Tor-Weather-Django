from django.db import models
from weatherapp.helpers import StringGenerator 
import datetime
import TorCtl.TorCtl
import socket
import base64
import re

# Supposedly required to make class methods.
# This is called on methods after their definitions.
# class Callable:
#    def __init__(self, anycallable):
#        self.__call__ = anycallable

class Adder:
    """An adder object is used to add Router, Subscription, or Subscriber
    objects to their respective databases with default values. All instance
    variables have default values stored in private class variables, but can
    be overriden in the constructor.

    @type time: datetime.datetime
    @ivar time: Datetime representing the default time to use for new Routers'
                last_seen fields, Subscribers' sub_date, and Subscriptions'
                last_changed. If unspecified in constructor, set to be 
                datetime.datetime.now() since, when a Router, Subscriber, or
                Subscription is added, the Router has just been seen, the 
                Subscriber has just subscribed, or the Subscription's Router has
                just changed (or we will act like it has, since this is when
                we start watching it). The time field of a specific Adder
                instance should be updated each time a consensus document
                is received with a call to update_time().
    @type router_welcomed: Bool
    @ivar router_welcomed: Default value to use for welcomed fields when
                           Router objects are added to the database. By
                           default, set to False.
    @type router_up: Bool
    @ivar router_up: Default value to use for up fields when Router objects are
                     added to the database. By default, set to True.
    @type subscriber_confirmed: Bool
    @ivar subscriber_confirmed: Default value to use for confirmed fields when
                                Subscriber objects are added to the databse. By
                                default, set to False.
    @type subscriber_confirm_auth: str
    @ivar subscriber_confirm_auth: Default value to use for confirm_auth fields
                                   when Subscriber objects are added to the 
                                   database. Note: An empty string will cause a
                                   new authorization code to be generated. By
                                   default, set to "".
    @type subscriber_unsubs_auth: str
    @ivar subscriber_unsubs_auth: Default value to use for unsubs_auth fields
                                  when Subscriber objects are added to the 
                                  database. Note: an empty string will cause a
                                  new authorization code to be generated. By
                                  default, set to "".
    @type subscriber_pref_auth: str
    @ivar subscriber_pref_auth: Default value to use for pref_auth fields when
                                Subscriber objects are added to the database.
                                Note: an empty string will cause a new
                                authorization code to be generated. By default,
                                set to "".
    @type subscription_emailed: Bool
    @ivar subscription_emailed: Default value to use for emailed fields when
                                Subscription objects are added to the database.
                                By default, set to False.
    @type subscription_triggered: Bool
    @ivar subscription_triggered: Default value to use for triggered fields
                                  when Subscription objects are added to the 
                                  database. By default, set to False.
    """
    
    __ROUTER_WELCOMED = False
    #__ROUTER_UP = True
    __SUBSCRIBER_CONFIRMED = False
    __SUBSCRIBER_CONFIRM_AUTH = ""
    __SUBSCRIBER_UNSUBS_AUTH = ""
    __SUBSCRUBER_PREF_AUTH = ""
    __SUBSCRIPTION_EMAILED = False
    __SUBSCRIPTION_TRIGGERED = False

    def __init__(self,
                 time = datetime.datetime.now(),
                 router_welcomed = __ROUTER_WELCOMED,
                 #router_up = __ROUTER_UP,
                 subscriber_confirmed = __SUBSCRIBER_CONFIRMED,
                 subscriber_confirm_auth = __SUBSCRIBER_CONFIRM_AUTH,
                 subscriber_unsubs_auth = __SUBSCRIBER_UNSUBS_AUTH,
                 subscriber_pref_auth = __SUBSCRIBER_PREF_AUTH,
                 subscription_emailed = __SUBSCRIPTION_EMAILED,
                 subscription_triggered = __SUBSCRIPTION_TRIGGERED):
        self.time = time
        self.welcomed_default = router_welcomed
        #self.up_default = router_up
        self.confirmed_default = subscriber_confirmed
        self.confirm_auth_default = subscriber_confirm_auth
        self.unsubs_auth_default = subscriber_unsubs_auth
        self.pref_auth_default = subscriber_pref_auth
        self.emailed_default = subscription_emailed
        self.triggered_default = subscription_triggered

    def update_time(self, time = datetime.datetime.now())
        """Updates the time field for this Adder instance. By default, updates
        to the current time, though a time can be passed to set it to a specific
        time.

        @type time: datetime.datetime
        @param time: Optional parameter to specify what time to update to.
                     Default value is obtained by datetime.datetime.now().
        """
        self.time = time

    def add_new_router(self, fingerprint, name,
                       welcomed = None,
                       last_seen = None,
                       up = None):
        """Adds a new Router object, handling variables that should always be
        set a certain way when a new Router object is added. The default
        variables (welcomed, last_seen, and up), which are stored as instance
        variables in the Adder class, can also be overriden in the method call.
    
        @type fingerprint: str
        @param fingerprint: Fingerprint of Router to be added.
        @type name: str
        @param name: Name of Router to be added ("Unnamed" if it doesn't
                     actually have one)
        @type welcomed: Bool
        @param welcomed: [Optional] Whether the router has been welcomed yet. 
                         Default value is False since a router needs to be
                         marked as stable before we want to welcome it, so we
                         should notice the router and add it to the database
                         long before it should be welcomed.
        @type last_seen: datetime.datetime
        @param last_seen: [Optional] Time when the router was last seen. 
                          Default value is the time for the Adder instance,
                          which should be updated each time a consensus
                          document is received.
        @type up: Bool
        @param up: [Optional] Whether the router was up when the last consensus
                   was received. Default value is True since it would not be
                   added to the Router database if it were not currently up.
    """
        # Note: Nones are used since self cannot be evaluated in the parameter
        # ----- list since it's defined in the parameter list. 
        if welcomed == None:    
            welcomed = self.welcomed_default
        if last_seen == None:   
            last_seen = self.time
        #if up == None:          
        #    up = self.up_default
            
        routr = Router(fingerprint = fingerprint, name = name,
                       welcomed = welcomed, last_seen = last_seen, up = up)
        routr.save()
        return routr

    def add_new_subscriber(email, router_id, 
                           confirmed = None,
                           confirm_auth = None, 
                           unsubs_auth = None, 
                           pref_auth = None,
                           sub_date = None):
        """Adds a new Subscriber object, handling variables that should always
        be set a certain way when a new Subscriber object is added. The default
        variables (confirmed, confirm_auth, unsubs_auth, pref_auth, and
        sub_date), which are stored as instance variables of the Adder class,
        can also be overriden in the method call.

        @type email: str
        @param email: The email address of the Subscriber to be added.
        @type router_id: int
        @param router_id: The Router database ID of the Router this Subscriber
                          is following.
        @type confirmed: Bool
        @param confirmed: [Optional] Whether the subscriber has confirmed yet.
                          Default value is False since a Subscriber object
                          should be added right when they fill out the initial
                          form, and so they should still have to receive an 
                          email and follow the confirmation link.
        @type confirm_auth: str
        @param confirm_auth: [Optional] Confirmation authorization code.
                             Default value is "", which will force the
                             generation of a new random key.
        @type unsubs_auth: str
        @param unsubs_auth: [Optional] Unsubscribe authorization code.
                            Default value is "", which will force the
                            generation of a new random key.
        @type pref_auth: str
        @param pref_auth: [Optional] Preferences authorization code.
                          Default value is "", which will force the generation
                          of a new random key.
        @type sub_date: datetime.datetime
        @param sub_date: [Optional] Time when the Subscriber subscribed.
                         Default value is the current time for the Adder
                         instance, which should be updated each time a
                         consensus document is received. This should be
                         sufficiently close to the actual time the user hits
                         subscribe, but maybe sub_date should be passed as
                         datetime.datetime.now() when this method is called to
                         be more precise.

        """
        # Note: Nones are used since self cannot be evaluated in the parameter
        # ----- list since it's defined in the parameter list.
        if confirmed = None:
            confirmed = self.confirmed_default
        if confirm_auth = None:
            confirm_auth = self.confirm_auth_default
        if unsubs_auth = None:
            unsubs_auth = self.unsubs_auth_default
        if pref_auth = None:
            pref_auth = self.pref_auth_default
        if sub_date = None:
            sub_date = self.time
        
        g = StringGenerator()
        if confirm_auth == "":
            confirm_auth = g.get_rand_string()
        if unsubs_auth == "":
            unsubs_auth = g.get_rand_string()
        if pref_auth == "":
            pref_auth = g.get_rand_string()
        
        subr = Subscriber(email = email, router = router_id,
                confirmed = confirmed, confirm_auth = confirm_auth,
                unsubs_auth = unsubs_auth, pref_auth = pref_auth, 
                sub_date = sub_date)
        subr.save()
        return subr
 
    def add_new_subscription(subscriber_id, name, threshold, grace_pd,
                             emailed = None, 
                             triggered = None,
                             last_changed = None):
        """Adds a new Subscription object, handling variables that should
        always be set a certain way when a new Subscription object is added.
        The default variables (emailed, triggered, and last_changed),
        which are stored as instance variables of the Adder class, can also be 
        overriden in the method call.

        @type subscriber_id: int
        @param subscriber_id: The Subscriber database ID of the Subscriber
                              subscribed to this subscription.
        @type name: str
        @param name: The type of this subscription.
        @type threshold: str
        @param threshold: The threshold of this subscription.
        @type grace_pd: int
        @param grace_pd: The grace period for this subscription before an email
                         is sent (measured in hours).
        @type emailed: Bool
        @param emailed: [Optional] Whether this subscription has had an email
                        sent out for it since it was last triggered. Default
                        value is False since the subscription was just created.
        @type triggered: Bool
        @param triggered: [Optional] Whether this subscription is currently
                          triggered. Default value is False since the
                          subscription was just created.
        @type last_changed: datetime.datetime
        @param last_changed: [Optional] The time when the status of the thing
                             being watched was last changed. Default value is
                             datetime.datetime.now() since an arbitrary value
                             has to be assigned.
        """

        if emailed = None:
            emailed = self.emailed_default
        if triggered = None:
            triggered = self.triggered_default
        if last_changed = None:
            last_changed = self.last_changed_default

        subn = Subscription(subscriber = subscriber_id, name = name,
                            threshold = threshold, grace_pd = grace_pd,
                            emailed = emailed, triggered = triggered,
                            last_changed = last_changed)
        subn.save()
        return subn



class Router(models.Model):
    """A model that stores information about every router on the Tor network.
    If a router hasn't been seen on the network for at least one year, it is
    removed from the database.
    
    @type fingerprint: str
    @ivar fingerprint: The router's fingerprint.
    @type name: str
    @ivar name: The name associated with the router.
    @type welcomed: bool
    @ivar welcomed: true if the router operater has received a welcome email,
                    false if they haven't.
    @type last_seen: datetime
    @ivar last_seen: The most recent time the router was listed on a consensus 
                     document. In the view that is processed when a consensus
                     document is received, will store the datetime when the
                     consensus document was received and so will be able to
                     check if the last_seen datetime matches with the consensus
                     datetime, informing whether the router is up.
    @type up: bool
    @ivar up: True if this router was up last time a new network consensus
              was published, false otherwise.
    """

    fingerprint = models.CharField(max_length=200)
    name = models.CharField(max_length=100)
    welcomed = models.BooleanField()
    last_seen = models.DateTimeField('date last seen')
    
    def is_up(date_of_last_consensus):
        """Returns whether the date_of_last_consensus datetime matches the
        last_seen datetime. Should be called in the view that processes events
        after a consensus is received.

        @type date_of_last_consensus: datetime.datetime
        @param date_of_last_consensus: Date of last consensus.
        """

        if last_seen = date_of_last_consensus:
            return True
        else:
            return False

    def __unicode__(self):
        return self.fingerprint

    # --- REPLACED WITH CLASS ADDER --------------------------
    #def add_new_router(fingerprint, name, welcomed=False, 
    #                   last_seen=datetime.datetime.now()):
    #    routr = Router(fingerprint = fingerprint, name = name, 
    #                   welcomed = welcomed)
    #    routr.save()
    #    return routr
    #
    # Supposedly makes add_new_router a class method.
    #add_new_router = Callable(add_new_router)
    # --------------------------------------------------------

class Subscriber(models.Model):
    """
    A model to store information about Tor Weather subscribers, including their
    authorization keys.

    @type email: EmailField
    @ivar email: The subscriber's email.
    @type router: ########################
    @ivar router: A foreign key link to the router model corresponding to the
        node this subscriber is watching.
    @type confirmed: boolean
    @ivar confirmed: true if the subscriber has confirmed the subscription by
        following the link in their confirmation email and false otherwise.
    @type confirm_auth: String
    @ivar confirm_auth: This user's confirmation key, which is incorporated into
        the confirmation url.
    @type unsubs_auth: String
    @ivar unsubs_auth: This user's unsubscribe key, which is incorporated into 
        the unsubscribe url.
    @type pref_auth: String
    @ivar pref_auth: The key for this user's Tor Weather preferences page.
    @type sub_date: datetime
    @ivar sub_date: The date this user subscribed to Tor Weather.
    """
    email = models.EmailField(max_length=75)
    router = models.ForeignKey(Router)
    confirmed = models.BooleanField()

    #change this when more is known?
    confirm_auth = models.CharField(max_length=250) 
    unsubs_auth = models.CharField(max_length=250)
    pref_auth = models.CharField(max_length=250)

    sub_date = models.DateTimeField()

    def __unicode__(self):
        return self.email

class SubscribeForm(forms.Form):
    """The form for subscribing"""
    email = forms.EmailField(max_length=75)
    router_id = forms.CharField(max_length=200)
    grace_pd = forms.IntegerField(default=1)

class Subscription(models.Model):
    """The model storing information about a specific subscription. Each type
    of email notification that a user selects generates a new subscription. 
    For instance, each subscriber who elects to be notified about low bandwidth
    will have a low_bandwidth subscription.
    
    @type subscriber: ######### (foreign key)
    @ivar subscriber: A link to the subscriber model representing the owner
        of this subscription.
    @type name: String
    @ivar name: The type of subscription.
    """
    subscriber = models.ForeignKey(Subscriber)
    name = models.CharField(max_length=200)
    threshold = models.CharField(max_length=200)
    grace_pd = models.IntegerField()
    emailed = models.BooleanField()
    triggered = models.BooleanField()
    last_changed = models.DateTimeField('date of last change')
    
    def __unicode__(self):
        return self.name

    def should_email()
        time_since_changed = datetime.datetime.now() - last_changed
        hours_since_changed = time_since_changed.hours / 3600
        if triggered and not emailed and \
                (hours_since_changed > grace_pd):
            return true
        else:
            return false

class PreferencesForm(forms.Form):
    """The form for changing preferences"""
    grace_pd = forms.IntegerField()

class CheckSubscriptions:
    """A class for checking and updating the various subscription types"""
    def __init__(self)
        self.pinger = TorPing()

    def check_all_down(self):
        """Check if all nodes with node_down subscriptions are up or down, and
        send emails and update subscription data as necessary."""

        #All node down subscriptions
        subscriptions = Subscription.objects.filter(name = "node_down")

        for subscription in subscriptions:
            is_up = self.pinger.ping(subscription.subscriber.router.fingerprint) 
            if is_up:
                if subscription.triggered:
                   subscription.triggered = False
                   subscription.last_changed = datetime.datetime.now()
            else:
                if subscription.triggered:
                    if subscription.should_email():
                        recipient = subscription.subscriber.email
                        Emailer.send_node_down_email(recipient)
                        subscription.emailed = True 
                else:
                    subscription.triggered = True
                    subscription.last_changed = datetime.datetime.now()
        return

    def check_out_of_date():
# -------------------------------------------------------------------------
# Put code here.
# -------------------------------------------------------------------------
        pass

    def check_below_bandwidth():
# -------------------------------------------------------------------------
# Put code here.
# -------------------------------------------------------------------------
        pass

    def check_earn_tshirt():
# -------------------------------------------------------------------------
# Put code here.
# -------------------------------------------------------------------------
        pass

class TorPing:
    "Check to see if various tor nodes respond to SSL hanshakes"
    def __init__(self, control_host = "127.0.0.1", control_port = 9051):

        "Keep the connection to the control port lying around"
        self.control_host = control_host
        self.control_port = control_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((control_host,control_port))
        except:
            #errormsg = "Could not connect to Tor control port" + \
                       "Is Tor running on %s with its control port opened on %s?" \
                        % (control_host, control_port)
            #logging.error(errormsg)
            #print >> sys.stderr, errormsg
            errormsg = "Could not connect to Tor control port" + \
                       "Is Tor running on %s with its control port opened on" +
                        " %s?" % (control_host, control_port)
            logging.error(errormsg)
            print >> sys.stderr, errormsg
            raise
        self.control = TorCtl.Connection(self.sock)
        self.control.authenticate(weather.config.authenticator)

    def __del__(self):
        self.sock.close()
        del self.sock
        self.sock = None                # prevents double deletion exceptions

        # it would be better to fix TorCtl!
        try:
            self.control.close()
        except:
            pass

        del self.control
        self.control = None
    
    "Need to re-include logging functionality" 
    def ping(self, nodeId):
        """See if this tor node is up by only asking Tor."""
        try:
            info = self.control.get_info(str("ns/id/" + nodeId))
        except TorCtl.ErrorReply, e:
            # If we're getting here, we're likely seeing:
            # ErrorReply: 552 Unrecognized key "ns/id/46D9..."
            # This means that the node isn't recognized by 
            return False

        except:
            return False

        # If we're here, we were able to fetch information about the router
        return True

class RouterUpdater:
    """A class for updating the Router table"""
    def __init__(self, control_host = "127.0.0.1", control_port = 9051):
        self.control_host = control_host
        self.control_port = control_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((control_host, control_port)) #add error rasing/handling
        self.control = TorCtl.Connection(self.sock)
        self.control.authenticate(config.authenticator)

    #We probably need this...see TorPing
    def __del__(self):
        self.sock.close()
        del self.sock
        self.sock = None

        try:
            self.control.close()
        except:
            pass
        
        del self.control
        self.control = None

    def update_all(self):
        """Add ORs we haven't seen before to the database and update the
        information of ORs that are already in the database."""

        #The dictionary returned from TorCtl
        desc_dict = self.control.get_info("desc/all-recent")

        #A list of the router descriptors in desc_dict
        desc_list = str(descriptor_dict.values()[0]).split("----End Signature----")
        
        #Make a list of tuples of all router fingerprints in descriptor with
        #whitespace removed and router names
        router_list= []

        for desc in desc_list:
            desc_lines = desc.split("\n")
            finger = ""
            for line in desc_lines:
                if line.startswith("opt fingerprint"):
                    finger = line[15:].replace(' ', '')
                if line.startswith("router "):
                    split_line = line.split()
                    name = split_line[1]

            #We ignore ORs that don't publish their fingerprints
            if not finger == "":
                router_list.append((finger, name))
        
        for router in router_list:
            is_up = False
            finger = router[0]
            name = router[1]
            try:
                control.get_info("ns/id/" + finger)
                is_up = True
            except:
                pass
            
            if is_up:
                try:
                    router_data = Router.objects.get(fingerprint = finger)
                    router_data.last_seen = datetime.datetime.now()
                    router_data.name = name
                except DoesNotExist:
                    #let's add it
                    new_router = Router(finger, name, False,
                                        datetime.datetime.now())
        return
