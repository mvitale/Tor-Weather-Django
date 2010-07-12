"""
The models module handles the bulk of Tor Weather's database management. The 
module contains three models that correspond to database tables (L{Subscriber}, 
L{Subscription}, and L{Router}) as well as two form classes (L{SubscribeForm} 
and L{PreferencesForm}), which specify the fields to appear on the sign-up 
and change preferences pages.
"""
from datetime import datetime
import base64
import os
import re
from copy import copy

from config import url_helper

from django.db import models
from django import forms

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
                    false if they haven't. Default value is C{False}.
    @type last_seen: datetime
    @ivar last_seen: The most recent time the router was listed on a consensus 
                     document. Default value is C{datetime.now()}.
    @type up: bool
    @ivar up: C{True} if this router was up last time a new network consensus
              was published, false otherwise. Default value is C{True}.
    @type exit: bool
    @ivar exit: C{True} if this router accepts exits to port 80, C{False} if
        not.
    """

    fingerprint = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=100, default = "Unnamed")
    welcomed = models.BooleanField(default=False)
    last_seen = models.DateTimeField(default=datetime.now)
    up = models.BooleanField(default=True)
    exit = models.BooleanField()

    def __unicode__(self):
        """Returns the fingerprint for this router as it's string representation
        
        @rtype: str
        @return: The router's fingerprint.
        """
        return self.fingerprint

    def printer(self):
        """Returns a description of this router. Meant to be used for testing
        purposes in the shell

        @rtype: str
        @return: A representation of this router's fields.
        """

        print 'Fingerprint: ' + self.fingerprint + \
              '\nName: ' + self.name + \
              '\nWelcomed: ' + str(self.welcomed) + \
              '\nLast Seen: ' + str(self.last_seen) + \
              '\nUp: ' + str(self.up) + \
              '\nExit: ' + str(self.exit)

class SubscriberManager(models.Manager):
    """In Django, each model class has at least one Manager (by default,
    there is one named 'objects' for each model). The Manager acts as the
    interface through which database query operations are provided to the 
    models. The SubscriberManager class is a custom Manager for the Subscriber
    model, which contains the method get_rand_string to generate a random
    string for user authentication keys."""

    @staticmethod
    def get_rand_string():
        """Returns a random, url-safe string of 24 characters (no '+' or '/'
        characters). The generated string does not end in '-'.
        
        @rtype: str
        @return: A randomly generated, 24 character string (url-safe).
        """

        r = base64.urlsafe_b64encode(os.urandom(18))

        # some email clients don't like URLs ending in -
        if r.endswith("-"):
            r = r.replace("-", "x")
        return r

          
class Subscriber(models.Model):
    """
    A model to store information about Tor Weather subscribers, including their
    authorization keys.

    @type email: str
    @ivar email: The subscriber's email.
    @type router: Router
    @ivar router: A foreign key link to the router model corresponding to the
        node this subscriber is watching.
    @type confirmed: bool
    @ivar confirmed: True if the subscriber has confirmed the subscription by
        following the link in their confirmation email and False otherwise. 
        Default value upon creation is C{False}.
    @type confirm_auth: str
    @ivar confirm_auth: This user's confirmation key, which is incorporated into
        the confirmation url.
    @type unsubs_auth: str
    @ivar unsubs_auth: This user's unsubscribe key, which is incorporated into 
        the unsubscribe url.
    @type pref_auth: str
    @ivar pref_auth: The key for this user's Tor Weather preferences page.
    @type sub_date: datetime.datetime
    @ivar sub_date: The date this user subscribed to Tor Weather. Default value
                    upon creation is datetime.now().
    @type objects: SubscriberManager()
    @cvar objects: The L{SubscriberManager} object that handles table-wide 
        database manipulation for this model.
    """
    email = models.EmailField(max_length=75)
    router = models.ForeignKey(Router)
    confirmed = models.BooleanField(default = False)
    confirm_auth = models.CharField(max_length=250, 
                    default=SubscriberManager.get_rand_string) 
    unsubs_auth = models.CharField(max_length=250, 
                    default=SubscriberManager.get_rand_string)
    pref_auth = models.CharField(max_length=250, 
                    default=SubscriberManager.get_rand_string)

    sub_date = models.DateTimeField(default=datetime.now)

    objects = SubscriberManager()

    def __unicode__(self):
        """Returns the Subscriber's email as the string representation for this 
        object.
        
        @rtype: str
        @return: The subscriber's email.
        """
        return self.email

    def has_node_down_sub(self):
        """Checks if this subscriber object has a node down subscription.

        @rtype: Bool
        @return: Whether a node down subscription exists for this subscriber.
        """

        try:
            NodeDownSub.objects.get(subscriber = self)
        except NodeDownSub.DoesNotExist:
            return False
        else:
            return True

    def has_version_sub(self):
        """Checks if this subscriber object has a version subscription.
        
        @rtype: Bool
        @return: Whether a version subscription exists for this subscriber.
        """

        try:
            VersionSub.objects.get(subscriber = self)
        except VersionSub.DoesNotExist:
            return False
        else:
            return True

    def has_bandwidth_sub(self):
        """Checks if this subscriber object has a bandwidth subscription.

        @rtype: Bool
        @return: Whether a bandwidth subscription exists for this subscriber.
        """

        try:
            BandwidthSub.objects.get(subscriber = self)
        except BandwidthSub.DoesNotExist:
            return False
        else:
            return True

    def has_t_shirt_sub(self):
        """Checks if this subscriber object has a t-shirt subscription.
        
        @rtype: Bool
        @return: Whether a t-shirt subscription exists for this subscriber.
        """

        try:
            TShirtSub.objects.get(subscriber = self)
        except TShirtSub.DoesNotExist:
            return False
        else:
            return True

    def get_preferences(self):
        """Returns a dictionary of preferences for the subscriber object.
        Key names are those used in the GenericForm, SubscribeForm, and
        PreferencesForm. This is mainly to be used to determine a user's
        current preferences in order to generate an initial preferences page.
        Checks the database for subscriptions corresponding to the subscriebr,
        and returns a dictionary of the settings of those subscriptions. The
        dictionary contains entries for all fields of all subscriptions
        subscribed to by the subscriber, but will not contain entries for
        fields of subscriptions not subscribed to (except for the "get_xxx"
        fields, which will always be defined for every subscription type).

        @rtype: Dict {str: str}
        @return: Dictionary of current preferences for this subscriber.
        """
        
        data = {}

        data['get_node_down'] = self.has_node_down_sub()
        if data['get_node_down']:
            n = NodeDownSub.objects.get(subscriber = self)
            data['node_down_grace_pd'] = n.grace_pd
        else:
            data['node_down_grace_pd'] = GenericForm._INIT_PREFIX + \
                    str(GenericForm._NODE_DOWN_GRACE_PD_INIT)

        data['get_version'] = self.has_version_sub()
        if data['get_version']:
            v = VersionSub.objects.get(subscriber = self)
            data['version_type'] = v.notify_type
        else:
            data['version_type'] = u'UNRECOMMENDED'

        data['get_band_low'] = self.has_bandwidth_sub()
        if data['get_band_low']:
            b = BandwidthSub.objects.get(subscriber = self)
            data['band_low_threshold'] = b.threshold
        else:
            data['band_low_threshold'] = GenericForm._INIT_PREFIX + \
                    str(GenericForm._BAND_LOW_THRESHOLD_INIT)

        data['get_t_shirt'] = self.has_t_shirt_sub()

        return data

    def printer(self):
        """Returns a description of this subscriber. Meant to be used for
        testing purposes in the shell

        @rtype: str
        @return: A representation of this subscriber's fields.
        """

        print 'Email: ' + self.email + \
              '\nRouter: ' + self.router.name + ' ' + \
                             self.router.fingerprint + \
              '\nConfirmed: ' + str(self.confirmed) + \
              '\nConfirm Auth: ' + self.confirm_auth + \
              '\nUnsubscribe Auth: ' + self.unsubs_auth + \
              '\nPreferences Auth: ' + self.pref_auth + \
              '\nSubscription Date: ' + str(self.sub_date)

class SubscriptionManager(models.Manager):
    """The custom Manager for the Subscription class. The Manager contains
    a method to get the number of hours since the time stored in the
    'last_changed' field in a Subscription object.
    """

    @staticmethod
    def hours_since_changed(last_changed):
        """Returns the time that has passed since the datetime parameter
        last_changed in hours.

        @type last_changed: datetime.datetime
        @param last_changed: The date and time of the most recent change
            for some flag.
        @rtype: int
        @return: The number of hours since last_changed.
        """
        time_since_changed = datetime.now() - last_changed
        hours_since_changed = (time_since_changed.hours * 24) + \
                              (time_since_changed.seconds / 3600)
        return hours_since_changed
    

class Subscription(models.Model):
    """The model storing information about a specific subscription. Each type
    of email notification that a user selects generates a new subscription. 
    For instance, each subscriber who elects to be notified about low bandwidth
    will have a low_bandwidth subscription.
    
    @ivar subscriber: A link to the subscriber model representing the owner
        of this subscription.
    @type emailed: bool
    @ivar emailed: True if the user has been emailed about the subscription
        (trigger must also be True), False if the user has not been emailed. 
        Default upon creation is C{False}.
    @type objects: SubscriptionManager()
    @cvar objects: The L{SubscriptionManager} object for this class, which 
        handles table-wide database manipulation for all Subscriptions. 
    """
    subscriber = models.ForeignKey(Subscriber)
    emailed = models.BooleanField(default=False)

    # In Django, Manager objects handle table-wide methods (i.e filtering)
    objects = SubscriptionManager()

    def printer(self):
        """Returns a description of this subscription. Meant to be used for
        testing purposes in the shell

        @rtype: str
        @return: A representation of this subscription's fields.
        """

        print 'Subscriber: ' + self.subscriber.email + ' ' + \
                             self.subscriber.router.name + ' ' + \
                             self.subscriber.router.fingerprint + \
              '\nEmailed: ' + str(self.emailed)

class NodeDownSub(Subscription):
    """A subscription class for node-down subscriptions, which send 
    notifications to the user if their node is down for the downtime grace
    period they specify. 

    @type triggered: bool
    @ivar triggered: C{True} if the node is down, C{False} if it is up.
    @type grace_pd: int
    @ivar grace_pd: The amount of time (hours) before a notification is sent
        after a node is seen down.
    @type last_changed: datetime
    @ivar last_changed: The datetime object representing the time the triggered
        flag was last changed.
    """
    triggered = models.BooleanField(default=False)
    grace_pd = models.IntegerField()
    last_changed = models.DateTimeField(default=datetime.now)

    def is_grace_passed(self):
        """Check if the grace period has passed for this subscription
        
        @rtype: bool
        @return: C{True} if C{triggered} and 
        C{SubscriptionManager.hours_since_changed()}, otherwise C{False}.
        """

        if self.triggered and SubscriptionManager.hours_since_changed() >= \
                grace_pd:
            return True
        else:
            return False

    def printer(self):
        """Returns a description of this subscription. Meant to be used for
        testing purposes in the shell

        @rtype: str
        @return: A representation of this subscription's fields.
        """
        
        print 'Node Down Subscription' + \
              '\nSubscriber: ' + self.subscriber.email + ' ' + \
              self.subscriber.router.name + ' ' + \
              self.subscriber.router.fingerprint + \
              '\nEmailed: ' + str(self.emailed) + \
              '\nTriggered: ' + str(self.triggered) + \
              '\nGrace Period: ' + str(self.grace_pd) + \
              '\nLast Changed: ' + str(self.last_changed)

class VersionSub(Subscription):
    """Subscription class for version notifications. Subscribers can choose
    between two notification types: OBSOLETE or UNRECOMMENDED. For OBSOLETE
    notifications, the user is sent an email if their router's version of Tor
    does not appear in the list of recommended versions (obtained via TorCtl).
    For UNRECOMMENDED notifications, the user is sent an email if their router's
    version of Tor is not the most recent stable (non-alpha/beta) version of
    Tor in the list of recommended versions.

    @type notify_type: str
    @ivar notify_type: Either UNRECOMMENDED (notify users if the router isn't 
        running the most recent stable version of Tor) or OBSOLETE (notify users
        if their router is running a version of Tor that doesn't appear on the
        list of recommended versions).
    """
    #only send notifications if the version is of type notify_type
    notify_type = models.CharField(max_length=250)

    def printer(self):
        """Returns a description of this subscription. Meant to be used for
        testing purposes in the shell

        @rtype: str
        @return: A representation of this subscription's fields.
        """
        
        print 'Version Subscription' + \
              '\nSubscriber: ' + self.subscriber.email + ' ' + \
              self.subscriber.router.name + ' ' + \
              self.subscriber.router.fingerprint + \
              '\nEmailed: ' + str(self.emailed) + \
              '\nNotify Type: ' + self.notify_type

class BandwidthSub(Subscription):    
    """Subscription class for low bandwidth notifications. Subscribers determine
    a threshold bandwidth in KB/s (default is 20KB/s). If the observed bandwidth
    field in the descriptor file for their router is ever below that threshold, 
    the user is sent a notification. According to the directory specifications,
    the observed bandwidth field "is an estimate of the capacity this server  
    can handle. The server remembers the max bandwidth sustained output over 
    any ten second period in the past day, and another sustained input. The 
    'observed' value is the lesser of these two numbers." An email is sent 
    as soon as we this observed bandwidth crosses the threshold (no grace pd).

    @type threshold: int
    @ivar threshold: The threshold for the bandwidth (in KB/s) that the user 
        specifies for receiving notifications.
    """
    threshold = models.IntegerField(default = 20)
    
    def printer(self):
        """Returns a description of this subscription. Meant to be used for
        testing purposes in the shell

        @rtype: str
        @return: A representation of this subscription's fields.
        """

        print 'Bandwidth Subscription' + \
              '\nSubscriber: ' + self.subscriber.email + ' ' + \
              self.subscriber.router.name + ' ' + \
              self.subscriber.router.fingerprint + \
              '\nEmailed: ' + str(self.emailed) + \
              '\nThreshold: ' + self.threshold

class TShirtSub(Subscription):
    """A subscription class for T-shirt notifications. An email is sent
    to the user if the router they're monitoring has earned them a T-shirt.
    The router must be running for 61 days (2 months). If it's an exit node,
    it's avg bandwidth must be at least 100 KB/s. Otherwise, it must be at 
    least 500 KB/s.

    @type triggered: bool
    @ivar triggered: C{True} if this router is up, 
    @type avg_bandwidth: int
    @ivar avg_bandwidth: The router's average bandwidth in KB/s
    @type last_changed: datetime
    @ivar last_changed: The datetime object representing the last time the 
        triggered flag was changed.
    """
    triggered = models.BooleanField(default = False)
    avg_bandwidth = models.IntegerField(default = 0)
    last_changed = models.DateTimeField(default = datetime.now)

    def get_hours_since_triggered(self):
        """Returns the time in hours that the router has been up."""
        if self.triggered == False:
            return 0
        time_since_triggered = datetime.now() - self.last_changed
        # timedelta objects only store days, seconds, and microseconds :(
        hours = time_since_triggered.seconds / 3600 + \
                time_since_triggered.days * 24
        return hours

    def should_email(hours_up):
        """Returns true if the router being watched has been up for 1464 hours
        (61 days, or approx 2 months). If it's an exit node, the avg bandwidth
        must be at or above 100 KB/s. If not, it must be >= 500 KB/s.
        
        @type hours_up: int
        @param hours_up: The hours that this router has been up (0 if the
            router was last seen down)
        @rtype: bool
        @return: C{True} if the user earned a T-shirt, C{False} if not.
        """
        if not self.emailed and self.triggered and hours_up >= 1464:
            if self.subscriber.router.exit:
                if self.avg_bandwidth >= 100:
                    return True
            else:
                if self.avg_bandwidth >= 500:
                    return True
        return False

    def printer(self):
        """Returns a description of this subscription. Meant to be used for   
        testing purposes in the shell

        @rtype: str
        @return: A representation of this subscription's fields.
        """
        
        print 'T-Shirt Subscription' + \
              '\nSubscriber: ' + self.subscriber.email + ' ' + \
              self.subscriber.router.name + ' ' + \
              self.subscriber.router.fingerprint + \
              '\nEmailed: ' + str(self.emailed) + \
              '\nTriggered: ' + str(self.triggered) + \
              '\nAverage Bandwidth: ' + str(self.avg_bandwidth) + \
              '\nLast Changed:' + str(self.last_changed)


class GenericForm(forms.Form):
    """The basic form class that is inherited by the SubscribeForm class
    and the PreferencesForm class.
   
    @type _GET_NODE_DOWN_INIT: Bool
    @cvar _GET_NODE_DOWN_INIT: The initial value of the get_node_down checkbox
        when the form is loaded.
    @type _GET_VERSION_INIT: Bool
    @cvar _GET_VERSION_INIT: The initial value of the get_version checkbox when
        the form is loaded.
    @type _GET_BANDLOW_INIT: Bool
    @cvar _GET_BANDLOW_INIT: The initial value of the get_band_low checkbox
        when the form is loaded.
    @type _NODE_DOWN_GRACE_PD_INIT: int
    @cvar _NODE_DOWN_GRACE_PD_INIT: The default initial node down grace pd (1 
        hr)
    @type _NODE_DOWN_GRACE_PD_MAX: int
    @cvar _NODE_DOWN_GRACE_PD_MAX: The maximum node down grace period in hours
    @type _NODE_DOWN_GRACE_PD_MIN: int
    @cvar _NODE_DOWN_GRACE_PD_MIN: The minimum node down grace period in hours
    @type _BAND_LOW_THRESHOLD_INIT: int
    @cvar _BAND_LOW_THRESHOLD_INIT: The initial low bandwidth threshold (kb/s)
    @type _BAND_LOW_THRESHOLD_MIN: int
    @cvar _BAND_LOW_THRESHOLD_MIN: The minimum low bandwidth threshold (kb/s)
    @type _BAND_LOW_THERSHOLD_MAX: int
    @cvar _BAND_LOW_THERSHOLD_MAX: The maximum low bandwidth threshold (KB/s)
    @type _INIT_PREFIX: str
    @cvar _INIT_PREFIX: The prefix for strings that display before user has
        entered data.
    @type _VERSION_INFO: str
    @cvar _VERSION_INFO: Help text for the version notification field.
    @type get_node_down: BooleanField
    @ivar get_node_down: C{True} if the user wants to subscribe to node down 
        notifications, C{False} if not.
    @type node_down_grace_pd: IntegerField, processed into int
    @ivar node_down_grace_pd: Time before receiving a node down notification in 
        hours. Default = 1. Range = 1-4500.
    @type get_version: BooleanField, processed into Bool
    @ivar get_version: C{True} if the user wants to receive version 
        notifications about their router, C{False} if not.
    @type version_type: ChoiceField, processed into str
    @ivar version_type: The type of version notifications the user 
        wants
    @type version_text: BooleanField
    @ivar version_text: Hidden field; used to display extra text in the form
        template without having to hardcode the text into the template.
    @type get_band_low: BooleanField, processed into Bool
    @ivar get_band_low: C{True} if the user wants to receive low bandwidth 
        notifications, C{False} if not.
    @type band_low_threshold: IntegerField, processed into int
    @ivar band_low_threshold: The user's threshold (in KB/s) for low bandwidth
        notifications. Default = 20 KB/s.
    @type get_t_shirt: BooleanField, processed into Bool
    @ivar get_t_shirt: C{True} if the user wants to receive a t-shirt 
        notification, C{False} if not.
    @type t_shirt_text: BooleanField
    @ivar t_shirt_text: Hidden field; used to display extra text in the form
        template without having to hardcode the text into the template.
    """
   
    """
    @type _GET_NODE_DOWN_INIT: Bool
    @cvar _GET_NODE_DOWN_INIT: Initial display value and default submission
        value of the L{get_node_down} checkbox.
    @type _GET_NODE_DOWN_LABEL: Str
    @cvar _GET_NODE_DOWN_LABEL: Text displayed next to L{get_node_down} 
        checkbox.
    @type _GET_NODE_DOWN_ID: Str
    @cvar _GET_NODE_DOWN_ID: HTML/CSS id for L{get_node_down} checkbox.
    @type _NODE_DOWN_GRACE_PD_INIT: int
    @cvar _NODE_DOWN_GRACE_PD_INIT: Initial display value and default
        submission value of the L{node_down_grace_pd} field.
    @type _NODE_DOWN_GRACE_PD_MAX: int
    @cvar _NODE_DOWN_GRACE_PD_MAX: Maximum allowed value for the
        L{node_down_grace_pd} field.
    @type _NODE_DOWN_GRACE_PD_MAX_DESC: Str
    @cvar _NODE_DOWN_GRACE_PD_MAX_DESC: English approximation of
        L{_NODE_DOWN_GRACE_PD_MAX} for display purposes.
    @type _NODE_DOWN_GRACE_PD_MIN: int
    @cvar _NODE_DOWN_GRACE_PD_MIN: Minimum allowed value for the 
        L{node_down_grace_pd} field.
    @type _NODE_DOWN_GRACE_PD_LABEL: Str
    @cvar _NODE_DOWN_GRACE_PD_LABEL: Text displayed above 
        L{node_down_grace_pd} checkbox.
    @type _NODE_DOWN_GRACE_PD_HELP_TEXT: Str
    @cvar _NODE_DOWN_GRACE_PD_HELP_TEXT: Text displayed next to 
        L{node_down_grace_pd} checkbox.
    
    @type _GET_VERSION_INIT: Bool
    @cvar _GET_VERSION_INIT: Initial display value and default submission 
        value of the L{get_version} checkbox.
    @type _GET_VERSION_LABEL: Str
    @cvar _GET_VERSION_LABEL: Text displayed next to L{get_version} checkbox.
    @type _GET_VERSION_ID: Str
    @cvar _GET_VERSION_ID: HTML/CSS id for L{get_version} checkbox.
    @type _VERSION_TYPE_LABEL:
    @type _VERSION_TYPE_CHOICE_1:
    @type _VERSION_TYPE_CHOICE_2:
    @type _VERSION_TYPE_CHOICES:
    @type _VERSION_INFO:

    @type _GET_BAND_LOW_INIT:
    @type _GET_BAND_LOW_LABEL:
    @type _GET_BAND_LOW_ID:
    @type _BAND_LOW_THRESHOLD_INIT:
    

    """
    
    
    
    # NOTE: Most places inherit the min, max, and default values for fields
    # from here, but one notable exception is in the javascript file when
    # checking if textboxes haven't been altered.
    _GET_NODE_DOWN_INIT = True
    _GET_NODE_DOWN_LABEL = 'Email me when the node is down'
    _NODE_DOWN_GRACE_PD_INIT = 1
    _NODE_DOWN_GRACE_PD_MAX = 4500
    _NODE_DOWN_GRACE_PD_MAX_DESC = ' (roughly six months)'
    _NODE_DOWN_GRACE_PD_MIN = 1
    _NODE_DOWN_GRACE_PD_LABEL = 'How many hours of downtime before we send a \
            notifcation?'
    _NODE_DOWN_GRACE_PD_HELP_TEXT = 'Enter a value between ' + \
            str(_NODE_DOWN_GRACE_PD_MIN) + ' and ' + \
            str(_NODE_DOWN_GRACE_PD_MAX) + _NODE_DOWN_GRACE_PD_MAX_DESC

    _GET_VERSION_INIT = False
    _GET_VERSION_LABEL = 'Email me when the node\'s Tor version is out of date'
    _VERSION_TYPE_LABEL = 'For what kind of updates would you like to be \
            notified?'
    _VERSION_TYPE_CHOICE_1 = (u'UNRECOMMENDED', u'Recommended Updates')
    _VERSION_TYPE_CHOICE_2 = (u'OBSOLETE', u'Required Updates')
    _VERSION_TYPE_CHOICES = (_VERSION_TYPE_CHOICE_1, _VERSION_TYPE_CHOICE_2)
    _VERSION_INFO = '<p><em>Recommended Updates:</em>  Emails when the router \
            is not running the most up-to-date stable version of Tor.</p> \
            <p><em>Required Updates:</em>  Emails when the router is running \
            an obsolete version of Tor.</p>'

    _GET_BAND_LOW_INIT = False
    _GET_BAND_LOW_LABEL = 'Email me when the router has low bandwidth capacity'
    _BAND_LOW_THRESHOLD_INIT = 20
    _BAND_LOW_THRESHOLD_MIN = 0
    _BAND_LOW_THRESHOLD_MAX = 100000
    _BAND_LOW_THRESHOLD_LABEL = 'For what citical bandwidth, in kB/s, should \
            we send notifications?'
    _BAND_LOW_THRESHOLD_HELP_TEXT = 'Enter a value between ' + \
            str(_BAND_LOW_THRESHOLD_MIN) + ' and ' + \
            str(_BAND_LOW_THRESHOLD_MAX)
   
    _GET_T_SHIRT_INIT = False
    _T_SHIRT_URL = 'https://www.torproject.org/tshirt.html.en'
    _GET_T_SHIRT_LABEL = 'Email me when my router has earned me a \
            <a href="' + _T_SHIRT_URL + '">Tor t-shirt</a>'
    _T_SHIRT_INFO = '<em>Note:</em> You must be the router\'s operator to \
            claim your T-shirt.'

    _INIT_PREFIX = 'Default value is '
    _CLASS_SHORT = 'short-input'
    _CLASS_DROPDOWN = 'dropdown-input'

    get_node_down = forms.BooleanField(initial=_GET_NODE_DOWN_INIT,
            required=False,
            label=_GET_NODE_DOWN_LABEL)
    node_down_grace_pd = forms.IntegerField(
            initial=_INIT_PREFIX + str(_NODE_DOWN_GRACE_PD_INIT),
            required=False,
            max_value=_NODE_DOWN_GRACE_PD_MAX,
            min_value=_NODE_DOWN_GRACE_PD_MIN,
            label=_NODE_DOWN_GRACE_PD_LABEL,
            help_text=_NODE_DOWN_GRACE_PD_HELP_TEXT,
            widget=forms.TextInput(attrs={'class':_CLASS_SHORT}))
    
    get_version = forms.BooleanField(initial=_GET_VERSION_INIT,
            required=False,
            label=_GET_VERSION_LABEL)
    version_text = forms.BooleanField(required=False,
            label= _VERSION_INFO)
    version_type = forms.ChoiceField(required=False,
            choices=(_VERSION_TYPE_CHOICES),
            label=_VERSION_TYPE_LABEL,
            widget=forms.Select(attrs={'class':_CLASS_DROPDOWN}))
    
    get_band_low = forms.BooleanField(initial=_GET_BAND_LOW_INIT,
            required=False,
            label=_GET_BAND_LOW_LABEL)
    band_low_threshold = forms.IntegerField(
            initial=_INIT_PREFIX + str(_BAND_LOW_THRESHOLD_INIT),
            required=False, max_value=_BAND_LOW_THRESHOLD_MAX,
            min_value=_BAND_LOW_THRESHOLD_MIN, 
            label=_BAND_LOW_THRESHOLD_LABEL,
            help_text=_BAND_LOW_THRESHOLD_HELP_TEXT,
            widget=forms.TextInput(attrs={'class':_CLASS_SHORT}))
    
    get_t_shirt = forms.BooleanField(initial=_GET_T_SHIRT_INIT, 
            required=False,
            label=_GET_T_SHIRT_LABEL)
    t_shirt_text = forms.BooleanField(required=False,
            label=_T_SHIRT_INFO) 

    @staticmethod
    def clean_post_data(post_data):
        """Checks if POST data contains fields that still say "Default value 
        is C{-DEFAULT-VALUE-}" or are left blank and returns a POST dictionary
        with those fields replaced with just C{-DEFAULT-VALUE-}. Also sets
        the field_name_manipulated fields to C{on} or C{off} depending on
        whether POST data has been manipulated at this stage (there is a
        hidden form field that stores this value, and the template renders
        a hidden input field, with val='true' if the hidden form field is true,
        and val='false' if the hidden form field is false; the javascript then
        will know to put 'Default value is _' for that field by referring to
        the hidden input field). Has no side-effects on the original POST 
        dictionary passed as an argument (which is immutable anyway). The 
        output POST data is meant to be passed into the GenericForm being
        created.
        
        @type post_data: QueryDict
        @param post_data: POST request data.
        @rtype: QueryDict
        @return: POST request data with "Default value is C{-DEFAULT-VALUE-}
            replaced with C{-DEFAULT-VALUE-}.
        """

        data = copy(post_data)

        if data['node_down_grace_pd'] == GenericForm._INIT_PREFIX + \
                str(GenericForm._NODE_DOWN_GRACE_PD_INIT) \
           or data['node_down_grace_pd'] == '' \
           or 'get_node_down' not in data:
            data['node_down_grace_pd'] = GenericForm._NODE_DOWN_GRACE_PD_INIT

        if data['band_low_threshold'] == GenericForm._INIT_PREFIX + \
                str(GenericForm._BAND_LOW_THRESHOLD_INIT) \
           or data['band_low_threshold'] == '' \
           or 'get_band_low' not in data:
            data['band_low_threshold'] = GenericForm._BAND_LOW_THRESHOLD_INIT  
        
        return data
 
    def check_if_sub_checked(self, data):
        """Throws a validation error if no subscriptions are checked. 
        Abstracted out of clean() so that there isn't any redundancy in 
        subclass clean() methods."""

        # Ensures that at least one subscription must be checked.
        if not (data['get_node_down'] or
                data['get_version'] or
                data['get_band_low'] or
                data['get_t_shirt']):
            raise forms.ValidationError('You must choose at least one \
                                         type of subscription!')

    def clean(self):
        """Calls the check_if_sub_checked to ensure that at least one 
        subscription type has been selected. (This is a Django thing, called
        every time the is_valid method is called on a GenericForm POST request).
                
        @return: The 'cleaned' data from the POST request.
        """
        self.check_if_sub_checked(self.cleaned_data)

        return self.cleaned_data

class SubscribeForm(GenericForm):
    """Inherits from L{GenericForm}. The SubscribeForm class contains
    all the fields in the GenericForm class and additional fields for 
    the user's email and the fingerprint of the router the user wants to
    monitor.
    
    @type email_1: EmailField
    @ivar email_1: A field for the user's email 
    @type email_2: EmailField
    @ivar email_2: A field for the user's email (enter twice for security)
    @type fingerprint: str
    @ivar fingerprint: The fingerprint of the router the user wants to 
        monitor.
    """
    _EMAIL_1_LABEL = 'Enter Email:'
    _EMAIL_MAX_LEN = 75
    _EMAIL_2_LABEL = 'Re-enter Email:'
    _FINGERPRINT_LABEL = 'Node Fingerprint:'
    _FINGERPRINT_MAX_LEN = 40
    _CLASS_EMAIL = 'email-input'
    _CLASS_LONG = 'long-input'

    email_1 = forms.EmailField(label=_EMAIL_1_LABEL,
            widget=forms.TextInput(attrs={'class':_CLASS_EMAIL}),
            max_length=_EMAIL_MAX_LEN)
    email_2 = forms.EmailField(label='Re-enter Email:',
            widget=forms.TextInput(attrs={'class':_CLASS_EMAIL}),
            max_length=_EMAIL_MAX_LEN)
    fingerprint = forms.CharField(label='Node Fingerprint:',
            widget=forms.TextInput(attrs={'class':_CLASS_LONG}),
            max_length=_FINGERPRINT_MAX_LEN)

    def clean(self):
        """Called when the is_valid method is evaluated for a SubscribeForm 
        after a POST request."""
        
        # Calls the same helper methods used in the GenericForm clean() method.
        data = self.cleaned_data
        GenericForm.check_if_sub_checked(self, data)

        # Makes sure email_1 and email_2 match and creates error messages
        # if they don't as well as deleting the cleaned data so that it isn't
        # erroneously used.
        if 'email_1' in data and 'email_2' in data:
            email_1 = data['email_1']
            email_2 = data['email_2']

            if not email_1 == email_2:
                msg = 'Email addresses must match.'
                self._errors['email_1'] = self.error_class([msg])
                self._errors['email_2'] = self.error_class([msg])
                
                del data['email_1']
                del data['email_2']
       
        return data

    def clean_fingerprint(self):
        """Uses Django's built-in 'clean' form processing functionality to
        test whether the fingerprint entered is a router we have in the
        current database, and presents an appropriate error message if it
        isn't (along with helpful information).
        """
        fingerprint = self.cleaned_data.get('fingerprint')
        fingerprint.replace(' ', '')

        if self.is_valid_router(fingerprint):
            return fingerprint
        else:
            info_extension = url_helper.get_fingerprint_info_ext(fingerprint)
            msg = 'We could not locate a Tor node with that fingerprint. \
                   (<a href=%s>More info</a>)' % info_extension
            raise forms.ValidationError(msg)

    def is_valid_router(self, fingerprint):
        """Helper function to check if a router exists in the database.
        """
        router_query_set = Router.objects.filter(fingerprint=fingerprint)

        if router_query_set.count() == 0:
            return False
        else:
            return True

    def create_subscriber(self):
        """Attempts to save the new subscriber, but throws a catchable error
        if a subscriber already exists with the given email and fingerprint.
        PRE-CONDITION: fingerprint is a valid fingerprint for a 
        router in the Router database.
        """

        email = self.cleaned_data['email_1']
        fingerprint = self.cleaned_data['fingerprint']
        router = Router.objects.get(fingerprint=fingerprint)

        # Get all subscribers that have both the email and fingerprint
        # entered in the form. 
        subscriber_query_set = Subscriber.objects.filter(email=email, 
                                    router__fingerprint=fingerprint)
        
        # Redirect the user if such a subscriber exists, else create one.
        if subscriber_query_set.count() > 0:
            subscriber = subscriber_query_set[0]
            url_extension = url_helper.get_error_ext('already_subscribed', 
                                               subscriber.pref_auth)
            raise Exception(url_extension)
            #raise UserAlreadyExistsError(url_extension)
        else:
            subscriber = Subscriber(email=email, router=router)
            subscriber.save()
            return subscriber
 
    def create_subscriptions(self, subscriber):
        """Create the subscriptions if they are specified.
        
        @type subscriber: Subscriber
        @param subscriber: The subscriber whose subscriptions are being saved.
        """
        # Create the various subscriptions if they are specified.
        if self.cleaned_data['get_node_down']:
            node_down_sub = NodeDownSub(subscriber=subscriber,
                    grace_pd=self.cleaned_data['node_down_grace_pd'])
            node_down_sub.save()
        if self.cleaned_data['get_version']:
            version_sub = VersionSub(subscriber=subscriber,
                    notify_type = self.cleaned_data['version_type'])
            version_sub.save()
        if self.cleaned_data['get_band_low']:
            band_low_sub = BandwidthSub(subscriber=subscriber,
                    threshold=self.cleaned_data['band_low_threshold'])
            band_low_sub.save()
        if self.cleaned_data['get_t_shirt']:
            t_shirt_sub = TShirtSub(subscriber=subscriber)
            t_shirt_sub.save()
         
class PreferencesForm(GenericForm):
    """The form for changing preferences, as displayed on the preferences page. 
    The form displays the user's current settings for all subscription types 
    (i.e. if they haven't selected a subscription type, the box for that field 
    is unchecked). The PreferencesForm form inherits L{GenericForm}.
    """
    
    _USER_INFO_STR = '<p><span>Email:</span> %s</p> \
            <p><span>Router name:</span> %s</p> \
            <p><span>Router id:</span> %s</p>'

    def __init__(self, user, data = None):
        if data == None:
            super(GenericForm, self).__init__(initial=user.get_preferences())
        else:
            super(GenericForm, self).__init__(data)
 
        self.user = user

        fingerprint_text = str(self.user.router.fingerprint)
        fingerprint_list = re.findall('.{4}', fingerprint_text)
        fingerprint_text = ' '.join(fingerprint_list)
        
        self.user_info = PreferencesForm._USER_INFO_STR % (self.user.email, \
                self.user.router.name, fingerprint_text)

    def change_subscriptions(self, old_data, new_data):
        """Change the subscriptions and options if they are specified.
        
        @type subscriber: Subscriber
        @param subscriber: The subscriber whose subscriptions are being saved.
        """

        # If there already was a subscription, get it and update it or delete
        # it depending on the current value.
        if old_data['get_node_down']:
            n = NodeDownSub.objects.get(subscriber = self.user)
            if new_data['get_node_down']:
                n.grace_pd = new_data['node_down_grace_pd']
                n.save()
            else:
                n.delete()
        # If there wasn't a subscription before and it is checked now, then 
        # make one.
        elif new_data['get_node_down']:
            n = NodeDownSub(subscriber=subscriber, 
                    grace_pd=new_data['node_down_grace_pd'])
            n.save()

        # If there already was a subscription, get it and update it or delete
        # it depending on the current value.
        if old_data['get_version']:
            v = VersionSub.objects.get(subscriber = self.user)
            if new_data['get_version']:
                v.notify_type = new_data['version_type']
                v.save()
            else:
                v.delete()
        # If there wasn't a subscription before and it is checked now, then 
        # make one.
        elif new_data['get_version']:
            v = VersionSub(subscriber=self.user, 
                    notify_type=new_data['version_type'])
            v.save()

        # If there already was a subscription, get it and update it or delete
        # it depending on the current value.
        if old_data['get_band_low']:
            b = BandwidthSub.objects.get(subscriber = self.user)
            if new_data['get_band_low']:
                b.threshold = new_data['band_low_threshold']
                b.save()
            else:
                b.delete()
        # If there wasn't a subscription before and it is checked now, then
        # make one.
        elif new_data['get_band_low']:
            b = BandwidthSub(subscriber=self.user,
                    threshold=new_data['band_low_threshold'])
            b.save()

        # If there already was a subscription, get it and delete it if it's no
        # longer selected.
        if old_data['get_t_shirt']:
            t = TShirtSub.objects.get(subscriber = self.user)
            if not new_data['get_t_shirt']:
                t.delete()
        # If there wasn't a subscription before and it is checked now, then
        # make one.
        elif new_data['get_t_shirt']:
            t = TShirtSub(subscriber=self.user)
            t.save()
