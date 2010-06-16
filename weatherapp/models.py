"""
The models module handles the bulk of Tor Weather. The module contains three
models that correspond to database tables (L{Subscriber}, L{Subscription}, and 
L{Router}) as well as two form classes (L{SubscribeForm} and
L{PreferencesForm}), which specify the fields to appear on the sign-up
and change preferences pages. The L{ModelAdder} class contains methods
to handle database population for the three models.
"""

from django.db import models
from django import forms
from weatherapp.helpers import StringGenerator 
from weatherapp.helpers import Emailer
from datetime import datetime
import base64

# Supposedly required to make class methods.
# This is called on methods after their definitions.
# class Callable:
#    def __init__(self, anycallable):
#        self.__call__ = anycallable

class ModelAdder:
    """An L{ModelAdder} object is used to add L{Router}, L{Subscription}, or
    L{Subscriber} objects to their respective databases with default values.
    All instance variables have default values stored in private class
    variables, but can be overriden in the constructor.

    @type time: datetime.datetime
    @ivar time: Datetime representing the default time to use for new 
                L{Router}s' L{Router.last_seen} fields, L{Subscriber}s'
                L{Subscriber.sub_date}, and L{Subscription}s' 
                L{Subscription.last_changed}. If unspecified in
                constructor, set to be C{datetime.datetime.now()} since, when a
                L{Router}, L{Subscriber}, or L{Subscription} is added, the
                L{Router} has just been seen, the L{Subscriber} has just
                subscribed, or the L{Subscription}'s L{Router} has
                just changed (or we will act like it has, since this is when
                we start watching it). The time field of a specific
                L{ModelAdder} instance should be updated each time a consensus
                document is received with a call to L{update_time()}.
    @type router_welcomed: Bool
    @ivar router_welcomed: Default value to use for welcomed fields when
                           L{Router} objects are added to the database. By
                           default, set to C{False}.
    @type router_up: Bool
    @ivar router_up: Default value to use for C{up} fields when L{Router} 
                     objects are added to the database. By default, set to 
                     C{True}.
    @type subscriber_confirmed: Bool
    @ivar subscriber_confirmed: Default value to use for C{confirmed} fields
                                when L{Subscriber} objects are added to the 
                                database. By default, set to C{False}.
    @type subscriber_confirm_auth: str
    @ivar subscriber_confirm_auth: Default value to use for C{confirm_auth}
                                   fields when L{Subscriber} objects are added
                                   to the database. Note: An empty string will
                                   cause a new authorization code to be
                                   generated. By default, set to C{""}.
    @type subscriber_unsubs_auth: str
    @ivar subscriber_unsubs_auth: Default value to use for C{unsubs_auth} 
                                  fields when L{Subscriber} objects are added
                                  to the database. Note: an empty string will
                                  cause a new authorization code to be
                                  generated. By default, set to C{""}.
    @type subscriber_pref_auth: str
    @ivar subscriber_pref_auth: Default value to use for C{pref_auth} fields
                                when L{Subscriber} objects are added to the
                                database. Note: an empty string will cause a 
                                new authorization code to be generated. By
                                default, set to C{""}.
    @type subscription_emailed: Bool
    @ivar subscription_emailed: Default value to use for C{emailed} fields when
                                L{Subscription} objects are added to the
                                database. By default, set to C{False}.
    @type subscription_triggered: Bool
    @ivar subscription_triggered: Default value to use for C{triggered} fields
                                  when L{Subscription} objects are added to the
                                  database. By default, set to C{False}.
    """
    
    _ROUTER_WELCOMED = False
    #_ROUTER_UP = True
    _SUBSCRIBER_CONFIRMED = False
    _SUBSCRIBER_CONFIRM_AUTH = ""
    _SUBSCRIBER_UNSUBS_AUTH = ""
    _SUBSCRIBER_PREF_AUTH = ""
    _SUBSCRIPTION_EMAILED = False
    _SUBSCRIPTION_TRIGGERED = False

    def __init__(self,
                 time = datetime.datetime.now(),
                 router_welcomed = _ROUTER_WELCOMED,
                 #router_up = _ROUTER_UP,
                 subscriber_confirmed = _SUBSCRIBER_CONFIRMED,
                 subscriber_confirm_auth = _SUBSCRIBER_CONFIRM_AUTH,
                 subscriber_unsubs_auth = _SUBSCRIBER_UNSUBS_AUTH,
                 subscriber_pref_auth = _SUBSCRIBER_PREF_AUTH,
                 subscription_emailed = _SUBSCRIPTION_EMAILED,
                 subscription_triggered = _SUBSCRIPTION_TRIGGERED):
        self.time = time
        self.welcomed_default = router_welcomed
        #self.up_default = router_up
        self.confirmed_default = subscriber_confirmed
        self.confirm_auth_default = subscriber_confirm_auth
        self.unsubs_auth_default = subscriber_unsubs_auth
        self.pref_auth_default = subscriber_pref_auth
        self.emailed_default = subscription_emailed
        self.triggered_default = subscription_triggered

    def update_time(self, time = None):
        """Updates the time field for this L{ModelAdder} instance. By default,
        updates to the current time, though a time can be passed to set it to a
        specific time.

        @type time: datetime.datetime
        @param time: Optional parameter to specify what time to update to.
                     Default value is obtained by C{datetime.datetime.now()}.
        """
        # Note: None is used since apparently the default values are evaluated
        # ----- only once when the function definition is read, so putting
        # ----- datetime.datetime.now() as a default parameter would be 
        # ----- disastrous.
        if time == None:
            time = datetime.datetime.now()

        self.time = time

    def add_new_router(self, fingerprint, name,
                       welcomed = None,
                       last_seen = None):
        """Adds a new L{Router} object, handling variables that should always 
        be set a certain way when a new L{Router} object is added. The default
        variables (C{welcomed} and C{last_seen}), which are stored as instance
        variables in the L{ModelAdder} class, can also be overriden in the
        method call.
    
        @type fingerprint: str
        @param fingerprint: Fingerprint of L{Router} to be added.
        @type name: str
        @param name: Name of L{Router} to be added (C{"Unnamed"} if it doesn't
                     actually have one)
        @type welcomed: Bool
        @param welcomed: [Optional] Whether the router has been welcomed yet. 
                         Default value is C{False} since a router needs to be
                         marked as stable before we want to welcome it, so we
                         should notice the router and add it to the database
                         long before it should be welcomed.
        @type last_seen: datetime.datetime
        @param last_seen: [Optional] Time when the router was last seen. 
                          Default value is the time for the L{ModelAdder}
                          instance, which should be updated each time a 
                          consensus document is received.
        @type up: Bool
        @param up: [Optional] Whether the router was up when the last consensus
                   was received. Default value is True since it would not be
                   added to the L{Router} database if it were not currently up.
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
                       welcomed = welcomed, last_seen = last_seen)
        routr.save()
        return routr

    def add_new_subscriber(email, router_id, 
                           confirmed = None,
                           confirm_auth = None, 
                           unsubs_auth = None, 
                           pref_auth = None,
                           sub_date = None):
        """Adds a new L{Subscriber} object, handling variables that should
        always be set a certain way when a new L{Subscriber} object is added.
        The default variables (C{confirmed}, C{confirm_auth}, C{unsubs_auth},
        C{pref_auth}, and C{sub_date}), which are stored as instance variables
        of the L{ModelAdder} class, can also be overriden in the method call.

        @type email: str
        @param email: The email address of the L{Subscriber} to be added.
        @type router_id: int
        @param router_id: The L{Router} database ID of the L{Router} this
                          L{Subscriber} is following.
        @type confirmed: Bool
        @param confirmed: [Optional] Whether the subscriber has confirmed yet.
                          Default value is C{False} since a L{Subscriber} 
                          object should be added right when they fill out the
                          initial form, and so they should still have to
                          receive an email and follow the confirmation link.
        @type confirm_auth: str
        @param confirm_auth: [Optional] Confirmation authorization code.
                             Default value is C{""}, which will force the
                             generation of a new random key.
        @type unsubs_auth: str
        @param unsubs_auth: [Optional] Unsubscribe authorization code.
                            Default value is C{""}, which will force the
                            generation of a new random key.
        @type pref_auth: str
        @param pref_auth: [Optional] Preferences authorization code.
                          Default value is C{""}, which will force the 
                          generation of a new random key.
        @type sub_date: datetime.datetime
        @param sub_date: [Optional] Time when the L{Subscriber} subscribed.
                         Default value is the current time for the
                         L{ModelAdder} instance, which should be updated each
                         time a consensus document is received. This should be
                         sufficiently close to the actual time the user hits
                         subscribe, but maybe sub_date should be passed as
                         datetime.datetime.now() when this method is called to
                         be more precise.

        """
        # Note: Nones are used since self cannot be evaluated in the parameter
        # ----- list since it's defined in the parameter list.
        if confirmed == None:
            confirmed = self.confirmed_default
        if confirm_auth == None:
            confirm_auth = self.confirm_auth_default
        if unsubs_auth == None:
            unsubs_auth = self.unsubs_auth_default
        if pref_auth == None:
            pref_auth = self.pref_auth_default
        if sub_date == None:
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
        which are stored as instance variables of the L{ModelAdder} class, can
        also be overriden in the method call.

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
        @type emailed: bool
        @param emailed: [Optional] Whether this subscription has had an email
                        sent out for it since it was last triggered. Default
                        value is False since the subscription was just created.
        @type triggered: bool
        @param triggered: [Optional] Whether this subscription is currently
                          triggered. Default value is False since the
                          subscription was just created.
        @type last_changed: datetime.datetime
        @param last_changed: [Optional] The time when the status of the thing
                             being watched was last changed. Default value is
                             datetime.datetime.now() since an arbitrary value
                             has to be assigned.
        """
        # Note: Nones are used since self cannot be evaluated in the parameter
        # ----- list since it's defined in the parameter list.
        if emailed == None:
            emailed = self.emailed_default
        if triggered == None:
            triggered = self.triggered_default
        if last_changed == None:
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

        if last_seen == date_of_last_consensus:
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

    @ivar email: The subscriber's email.
    @ivar router: A foreign key link to the router model corresponding to the
        node this subscriber is watching.
    @type confirmed: bool
    @ivar confirmed: True if the subscriber has confirmed the subscription by
        following the link in their confirmation email and False otherwise.
    @type confirm_auth: str
    @ivar confirm_auth: This user's confirmation key, which is incorporated into
        the confirmation url.
    @type unsubs_auth: str
    @ivar unsubs_auth: This user's unsubscribe key, which is incorporated into 
        the unsubscribe url.
    @type pref_auth: str
    @ivar pref_auth: The key for this user's Tor Weather preferences page.
    @type sub_date: datetime.datetime
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

class Subscription(models.Model):
    """The model storing information about a specific subscription. Each type
    of email notification that a user selects generates a new subscription. 
    For instance, each subscriber who elects to be notified about low bandwidth
    will have a low_bandwidth subscription.
    
    @type subscriber: ######### (foreign key)
    @ivar subscriber: A link to the subscriber model representing the owner
        of this subscription.
    @type name: str
    @ivar name: The type of subscription.
    @type threshold: str
    @ivar threshold: The threshold for sending a notification (i.e. send a 
        notification if the version is obsolete vs. out of date; depends on 
        subscription type)
    @type grace_pd: int
    @ivar grace_pd: The amount of time (hours) before a notification is sent
        after a subscription type is triggered.
    @type emailed: bool
    @ivar emailed: True if the user has been emailed about the subscription
        (trigger must also be True), False if the user has not been emailed.
    @type triggered: bool
    @ivar triggered: True if the threshold has been passed for this 
        subscription/the conditions to send a notification are met, False
        if not.
    @type last_changed: datetime.datetime
    @ivar last_changed: The most recent datetime when the trigger field 
        was changed.
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

    def should_email():
        time_since_changed = datetime.now() - last_changed
        hours_since_changed = time_since_changed.seconds / 3600
        if triggered and not emailed and \
                (hours_since_changed > grace_pd):
            return True
        else:
            return False

class SubscribeForm(forms.Form):
    """The form for a new subscriber. The form includes an email field, 
    a node fingerprint field, and a field to specify the hours of downtime 
    before receiving a notification.


    @ivar email: A field for the user's email address
    @ivar fingerprint: A field for the fingerprint (node ID) corresponding 
        to the node the user wants to monitor
    @ivar grace_pd: A field for the hours of downtime the user specifies
        before being notified via email"""

    # widget attributes are modified here to customize the form
    email = forms.EmailField(widget=forms.TextInput(attrs={'size':'50', 
        'value' : 'Enter a valid email address', 'onClick' : 'if (this.value'+\
        '=="Enter a valid email address") {this.value=""}'}))
    fingerprint = forms.CharField(widget=forms.TextInput(attrs={'size':'50',
        'value' : 'Enter one Tor node ID', 'onClick' : 'if (this.value' +\
        '=="Enter one Tor node ID") {this.value=""}'}))
    grace_pd = forms.IntegerField(widget=forms.TextInput(attrs={'size':'50',
        'value' : 'Default is 1 hour, enter up to 8760 (1 year)', 'onClick' :
        'if (this.value=="Default is 1 hour, enter up to 8760 (1 year)") '+\
        '{this.value=""}'}))

class PreferencesForm(forms.Form):
    """The form for changing preferences.

    @ivar grace_pd: A fiend for the user to specify the hours of 
        downtime before an email notification is sent"""

    grace_pd = forms.IntegerField(widget=forms.TextInput(attrs={'size':'50'}))
"""
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
            #"Is Tor running on %s with its control port opened on %s?" \
                        % (control_host, control_port)
            #           "Is Tor running on %s with its control port opened on %s?" \
            #            % (control_host, control_port)
            #logging.error(errormsg)
            #print >> sys.stderr, errormsg
            errormsg = "Could not connect to Tor control port" + \
                       "Is Tor running on %s with its control port opened" + \
                        " on %s?" % (control_host, control_port)
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
        """ """See if this tor node is up by only asking Tor.""" """
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
"""
