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
from django.core import validators
from django.core.exceptions import ValidationError

class Router(models.Model):
    """Model for Tor network routers. Django uses class variables to specify
    model fields, but these fields are practically used and thought of as
    instance variables, so this documentation will refer to them as such.
    
    document this

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
    
    _FINGERPRINT_MAX_LEN = 40
    _NAME_MAX_LEN = 100
    _NAME_DEFAULT = "Unnamed"
    _WELCOMED_DEFAULT = False
    _LAST_SEEN_DEFAULT = datetime.now
    _UP_DEFAULT = True

    fingerprint = models.CharField(max_length=_FINGERPRINT_MAX_LEN, unique=True)
    name = models.CharField(max_length=_NAME_MAX_LEN, default=_NAME_DEFAULT)
    welcomed = models.BooleanField(default=_WELCOMED_DEFAULT)
    last_seen = models.DateTimeField(default=_LAST_SEEN_DEFAULT)
    up = models.BooleanField(default=_UP_DEFAULT)
    exit = models.BooleanField()

    def __unicode__(self):
        """Returns a simple description of this L{Router}.
        
        @rtype: str
        @return: Simple description of L{Router} object.
        """
        return self.name + ": " + self.spaced_fingerprint()

    def spaced_fingerprint(self):
        """Returns the fingerprint for this router as a string with spaces
        inserted every 4 characters.
        
        @rtype: str
        @return: The router's fingerprint with spaces inserted.
        """

        return ' '.join(re.findall('.{4}', str(self.fingerprint)))

    def get_string(self):
        """Returns a string representation of the name and fingerprint of
        this router. Ex: 'WesCSTor (id: 4094 8034 ...)'

        @rtype: str
        @return: name/fingerprint display.
        """

        if self.name == 'Unnamed':
            return '(id: ' + self.spaced_fingerprint() + ')'
        else:
            return self.name + '(id: ' + self.spaced_fingerprint() + ')'

    def __repr__(self):
        return 'Fingerprint: ' + self.fingerprint + \
                '\nName: ' + self.name + \
                '\nWelcomed: ' + str(self.welcomed) + \
                '\nLast Seen: ' + str(self.last_seen) + \
                '\nUp: ' + str(self.up) + \
                '\nExit: ' + str(self.exit)

    def more_info(self):
        """Returns a string description of this L{Router}. Meant to be 
        used for testing purposes in the shell, and is used to display
        more info than the basic string representation returned by
        __unicode__.

        @rtype: str
        @return: A representation of this L{Router}'s fields.
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
        """Returns the Subscriber's email as the string representation for 
        this object.
        
        @rtype: str
        @return: The subscriber's email.
        """
        return self.email

    def has_node_down_sub(self):
        """Checks if this subscriber object has a node down subscription.

        @rtype: bool
        @return: Whether a node down subscription exists for this subscriber.
        """
        
        return self._has_sub_type('NodeDownSub')

    def has_version_sub(self):
        """Checks if this subscriber object has a version subscription.
        
        @rtype: bool
        @return: Whether a version subscription exists for this subscriber.
        """

        return self._has_sub_type('VersionSub')

    def has_bandwidth_sub(self):
        """Checks if this subscriber object has a bandwidth subscription.

        @rtype: bool
        @return: Whether a bandwidth subscription exists for this subscriber.
        """

        return self._has_sub_type('BandwidthSub')

    def has_t_shirt_sub(self):
        """Checks if this subscriber object has a t-shirt subscription.
        
        @rtype: bool
        @return: Whether a t-shirt subscription exists for this subscriber.
        """

        return self._has_sub_type('TShirtSub')

    def _has_sub_type(self, sub_type):
        """Checks if this subscriber object has a subscription of C{sub_type}.

        @type sub_type: str
        @param sub_type: The type of subscription to check. This must   
                         be the exact name of a valid subscription type.

        @rtype: bool
        @return: C{True} if this subscriber object has a subscription of 
                 C{sub_type}, C{False} otherwise. If C{sub_type} is not a 
                 valid subscription type name, returns C{False}.
        """

        if sub_type == 'NodeDownSub':
            sub = NodeDownSub
        elif sub_type == 'VersionSub':
            sub = VersionSub
        elif sub_type == 'BandwidthSub':
            sub = BandwidthSub
        elif sub_type == 'TShirtSub':
            sub = TShirtSub
        else:
            return False
   
        try:
            sub.objects.get(subscriber = self)
        except sub.DoesNotExist:
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

    def more_info(self):
        """Returns a string description of this L{Subscriber}. Meant to be 
        used for testing purposes in the shell, and is used to display
        more info than the basic string representation returned by
        __unicode__.

        @rtype: str
        @return: A representation of this L{Subscriber}'s fields.
        """

        return 'Email: ' + self.email + \
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

    def more_info(self):
        """Returns a string description of this subscription. Meant to be 
        used for testing purposes in the shell, and is used to display
        more info than the basic string representation returned by
        __unicode__.

        @rtype: str
        @return: A representation of this L{Subscription}'s fields.
        """

        return 'Subscriber: ' + self.subscriber.email + ' ' + \
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
        C{SubscriptionManager.hours_since_changed()} >= C{grace_pd}, otherwise
        C{False}.
        """

        if self.triggered and SubscriptionManager.hours_since_changed() >= \
                grace_pd:
            return True
        else:
            return False

    def more_info(self):
        """Returns a string description of this L{NodeDownSub}. Meant to be 
        used for testing purposes in the shell, and is used to display
        more info than the basic string representation returned by
        __unicode__.

        @rtype: str
        @return: A representation of this L{NodeDownSub}'s fields.
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
    For UNRECOMMENDED notifications, the user is sent an email if their  
    router's version of Tor is not the most recent stable (non-alpha/beta)   
    version of Tor in the list of recommended versions.

    @type notify_type: str
    @ivar notify_type: Either UNRECOMMENDED (notify users if the router isn't 
        running the most recent stable version of Tor) or OBSOLETE (notify 
        users
        if their router is running a version of Tor that doesn't appear on the
        list of recommended versions).
    """
    #only send notifications if the version is of type notify_type 
    notify_type = models.CharField(max_length=250)

    def more_info(self):
        """Returns a string description of this L{VersionSub}. Meant to be 
        used for testing purposes in the shell, and is used to display
        more info than the basic string representation returned by
        __unicode__.

        @rtype: str
        @return: A representation of this L{VersionSub}'s fields.
        """
        
        print 'Version Subscription' + \
              '\nSubscriber: ' + self.subscriber.email + ' ' + \
              self.subscriber.router.name + ' ' + \
              self.subscriber.router.fingerprint + \
              '\nEmailed: ' + str(self.emailed) + \
              '\nNotify Type: ' + self.notify_type

class BandwidthSub(Subscription):    
    """Subscription class for low bandwidth notifications. Subscribers 
    determine a threshold bandwidth in KB/s (default is 20KB/s). If the 
    observed bandwidth field in the descriptor file for their router is ever   
    below that threshold, the user is sent a notification. According to the 
    directory specifications, the observed bandwidth field "is an estimate of 
    the capacity this server can handle. The server remembers the max 
    bandwidth sustained output over any ten second period in the past day, and 
    another sustained input. The 'observed' value is the lesser of these two 
    numbers." An email is sent as soon as we this observed bandwidth crosses 
    the threshold (no grace pd).

    @type threshold: int
    @ivar threshold: The threshold for the bandwidth (in KB/s) that the user 
        specifies for receiving notifications.
    """
    threshold = models.IntegerField(default = 20)
    
    def more_ino(self):
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

    def should_email(self, hours_up):
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

    def more_info(self):
        """Returns a string description of this L{TShirtSub}. Meant to be 
        used for testing purposes in the shell, and is used to display
        more info than the basic string representation returned by
        __unicode__.

        @rtype: str
        @return: A representation of this L{TShirtSub}'s fields.
        """
        
        print 'T-Shirt Subscription' + \
              '\nSubscriber: ' + self.subscriber.email + ' ' + \
              self.subscriber.router.name + ' ' + \
              self.subscriber.router.fingerprint + \
              '\nEmailed: ' + str(self.emailed) + \
              '\nTriggered: ' + str(self.triggered) + \
              '\nAverage Bandwidth: ' + str(self.avg_bandwidth) + \
              '\nLast Changed:' + str(self.last_changed)

class PrefixedIntegerField(forms.IntegerField):
    """An Integer Field that accepts input of the form "-prefix- -integer-"
    and parses it as simply -integer- in its to_python method. Replaces the
    previous process of overwriting post data, which was an ugly workaround.
    A PrefixedIntegerField will not accept empty input, but will throw a
    validationerror specifying that it was left empty, so that this error can
    be intercepted and dealth with cleanly.
    """

    _PREFIX = 'Default value is '

    default_error_messages = {
        'invalid': 'Enter a whole number.',
        'max_value': 'Ensure this value is less than or equal to \
                %(limit_value)s.',
        'min_value': 'Ensure this value is greater than or equal to \
                %(limit_value)s.',
        'empty': 'yo, dawg; I am empty and no user should see this error',
    }

    def __init__(self, max_value=None, min_value=None, *args, **kwargs):
        forms.IntegerField.__init__(self, *args, **kwargs)

        if max_value is not None:
            self.validators.append(validators.MaxValueValidator(max_value))
        if min_value is not None:
            self.validators.append(validators.MinValueValidator(min_value))

    def to_python(self, value):
        prefix = PrefixedIntegerField._PREFIX

        if value == '':
            raise ValidationError(self.error_messages['empty'])

        try:
            if value.startswith(prefix):
                value = int(forms.IntegerField.to_python(self, 
                    value[len(prefix):]))
            else:
                value = int(forms.IntegerField.to_python(self,
                                                value))
        except (ValueError, TypeError):
            raise ValidationError(self.error_messages['invalid'])

        return value

class GenericForm(forms.Form):
    """The basic form class that is inherited by the SubscribeForm class
    and the PreferencesForm class. Class variables specifying the types of 
    fields that instances of GenericForm receive are labeled as instance
    variables in this epydoc documentation since the specifications for fields
    can be thought of as the fields that act like instance variables.
   
    @type _GET_NODE_DOWN_INIT: bool
    @cvar _GET_NODE_DOWN_INIT: Initial display value and default submission
        value of the L{get_node_down} checkbox.
    @type _GET_NODE_DOWN_LABEL: str
    @cvar _GET_NODE_DOWN_LABEL: Text displayed next to L{get_node_down} 
        checkbox.
    @type _NODE_DOWN_GRACE_PD_INIT: int
    @cvar _NODE_DOWN_GRACE_PD_INIT: Initial display value and default
        submission value of the L{node_down_grace_pd} field.
    @type _NODE_DOWN_GRACE_PD_MAX: int
    @cvar _NODE_DOWN_GRACE_PD_MAX: Maximum allowed value for the
        L{node_down_grace_pd} field.
    @type _NODE_DOWN_GRACE_PD_MAX_DESC: str
    @cvar _NODE_DOWN_GRACE_PD_MAX_DESC: English approximation of
        L{_NODE_DOWN_GRACE_PD_MAX} for display purposes.
    @type _NODE_DOWN_GRACE_PD_MIN: int
    @cvar _NODE_DOWN_GRACE_PD_MIN: Minimum allowed value for the 
        L{node_down_grace_pd} field.
    @type _NODE_DOWN_GRACE_PD_LABEL: str
    @cvar _NODE_DOWN_GRACE_PD_LABEL: Text displayed above 
        L{node_down_grace_pd} checkbox.
    @type _NODE_DOWN_GRACE_PD_HELP_TEXT: str
    @cvar _NODE_DOWN_GRACE_PD_HELP_TEXT: Text displayed next to 
        L{node_down_grace_pd} checkbox.
    
    @type _GET_VERSION_INIT: bool
    @cvar _GET_VERSION_INIT: Initial display value and default submission 
        value of the L{get_version} checkbox.
    @type _GET_VERSION_LABEL: str
    @cvar _GET_VERSION_LABEL: Text displayed next to L{get_version} checkbox.
    @type _VERSION_TYPE_CHOICE_1: str
    @cvar _VERSION_TYPE_CHOICE_1: Backend name for the first choice of the
        L{version_type} field.
    @type _VERSION_TYPE_CHOICE_1_H: str
    @cvar _VERSION_TYPE_CHOICE_1_H: Frontend (human readable) name for the
        first choice of the L{version_type} field.
    @type _VERSION_TYPE_CHOICE_2: str
    @cvar _VERSION_TYPE_CHOICE_2: Backend name for the second choice of the 
        L{version_type} field.
    @type _VERSION_TYPE_CHOICE_2_H: str
    @cvar _VERSION_TYPE_CHOICE_2_H: Frontend (human readable) name for the
        second choice of the L{version_type} field.
    @type _VERSION_TYPE_CHOICES: list [tuple (str)]
    @cvar _VERSION_TYPE_CHOICES: List of tuples of backend and frontend names
        for each choice of the L{version_type} field.
    @type _VERSION_TYPE_INIT: str
    @cvar _VERSION_TYPE_INIT: Initial display value of the L{version_type} 
        field.
    @type _VERSION_INFO: str
    @cvar _VERSION_INFO: Text explaining the version subscription,  displayed
        in the expandable version section of the form, with HTML enabled.

    @type _GET_BAND_LOW_INIT: bool
    @cvar _GET_BAND_LOW_INIT: Initial display value and default submission
        value of the L{get_version} checkbox.
    @type _GET_BAND_LOW_LABEL: str
    @cvar _GET_BAND_LOW_LABEL: Text displayed next to L{get_version} checkbox.
    @type _BAND_LOW_THRESHOLD_INIT: int
    @cvar _BAND_LOW_THRESHOLD_INIT: Initial display value and default
        submission value of the L{band_low_threshold} field.
    @type _BAND_LOW_THRESHOLD_MIN: int
    @cvar _BAND_LOW_THRESHOLD_MIN: Minimum allowed value for the 
        L{band_low_threshold} field.
    @type _BAND_LOW_THRESHOLD_MAX: int
    @cvar _BAND_LOW_THRESHOLD_MAX: Maximum allowed value for the 
        L{band_low_threshold} field.
    @type _BAND_LOW_THRESHOLD_LABEL: str
    @cvar _BAND_LOW_THRESHOLD_LABEL: Text displayed above the
        L{band_low_threshold} field.
    @type _BAND_LOW_THRESHOLD_HELP_TEXT: str
    @cvar _BAND_LOW_THRESHOLD_HELP_TEXT: Text displayed next to the
        L{band_low_threshold} field.

    @type _T_SHIRT_URL: str
    @cvar _T_SHIRT_URL: URL for information about T-Shirts on Tor wesbite
    @type _GET_T_SHIRT_LABEL: str
    @cvar _GET_T_SHIRT_LABEL: Text displayed above the L{get_t_shirt} checkbox.
    @type _GET_T_SHIRT_INIT: bool
    @cvar _GET_T_SHIRT_INIT: Initial display value and default submission 
        value of the L{get_t_shirt} checkbox.
    @type _T_SHIRT_INFO: str
    @cvar _T_SHIRT_INFO: Text explaining the t-shirt subscription, displayed
        in the expandable version section of the form, with HTML enabled.

    @type _INIT_PREFIX: str
    @cvar _INIT_PREFIX: Prefix for display of default values.
    @type _CLASS_SHORT: str
    @cvar _CLASS_SHORT: HTML/CSS class to use for integer input fields.
    @type _CLASS_RADIO: str
    @cvar _CLASS_RADIO: HTML/CSS class to use for Radio button lists.
    @type _CLASS_CHECK: str
    @cvar _CLASS_CHECK: HTML/CSS class to use for checkboxes.
    @type _INIT_MAPPING: dict {string: various}
    @cvar _INIT_MAPPING: Dictionary of initial values for fields in 
        L{GenericForm}. Points to each of the fields' _XXX_INIT fields.

    @type get_node_down: forms.BooleanField
    @ivar get_node_down: Checkbox letting users choose to subscribe to a
        L{NodeDownSub}.
    @type node_down_grace_pd: PrefixedIntegerField
    @ivar node_down_grace_pd: Integer field (displaying prefix) letting users
        specify their grace period for a L{NodeDownSub}.

    @type get_version: forms.BooleanField
    @ivar get_version: Checkbox letting users choose to subscribe to a 
        L{VersionSub}.
    @type version_type: forms.ChoiceField
    @ivar version_type: Radio button list letting users choose the type of
        L{VersionSub} to subscribe to.
    
    @type get_band_low: forms.BooleanField
    @ivar get_band_low: Checkbox letting users choose to subscribe to a
        L{BandwidthSub}.
    @type band_low_threshold: PrefixedIntegerField
    @ivar band_low_threshold: Integer field (displaying prefix) letting users
        specify their threshold for a L{BandwidthSub}.

    @type get_t_shirt: forms.BooleanField
    @ivar get_t_shirt: Checkbox letting users choose to subscribe to a 
        L{TShirtSub}.
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
    _VERSION_TYPE_CHOICE_1 = 'UNRECOMMENDED'
    _VERSION_TYPE_CHOICE_1_H = 'Recommended Updates'
    _VERSION_TYPE_CHOICE_2 = 'OBSOLETE'
    _VERSION_TYPE_CHOICE_2_H = 'Required Updates'
    _VERSION_TYPE_CHOICES = [(_VERSION_TYPE_CHOICE_1, _VERSION_TYPE_CHOICE_1_H),
                             (_VERSION_TYPE_CHOICE_2, _VERSION_TYPE_CHOICE_2_H)]
    _VERSION_TYPE_INIT = _VERSION_TYPE_CHOICE_1
    _VERSION_SECTION_INFO = '<p><em>Recommended Updates:</em>  Emails when\
    the router is not running the most up-to-date stable version of Tor.</p> \
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
    _GET_T_SHIRT_LABEL = 'Email me when my router has earned me a \
            <a target=_BLANK href="' + url_helper.get_t_shirt_url() + \
            '">Tor t-shirt</a>'
    _T_SHIRT_SECTION_INFO = '<em>Note:</em> You must be the router\'s \
    operator to claim your T-shirt.'

    _INIT_PREFIX = 'Default value is '
    _CLASS_SHORT = 'short-input'
    _CLASS_RADIO = 'radio-list'
    _CLASS_CHECK = 'checkbox-input'
    _INIT_MAPPING = {'get_node_down': _GET_NODE_DOWN_INIT,
                     'node_down_grace_pd': _INIT_PREFIX + \
                             str(_NODE_DOWN_GRACE_PD_INIT),
                     'get_version': _GET_VERSION_INIT,
                     'version_type': _VERSION_TYPE_INIT,
                     'get_band_low': _GET_BAND_LOW_INIT,
                     'band_low_threshold': _INIT_PREFIX + \
                             str(_BAND_LOW_THRESHOLD_INIT),
                     'get_t_shirt': _GET_T_SHIRT_INIT}

    # These variables look like class variables, but are actually Django
    # shorthand for instance variables. Upon __init__, these fields will
    # be generated in instance's list of fields.
    get_node_down = forms.BooleanField(required=False,
            label=_GET_NODE_DOWN_LABEL,
            widget=forms.CheckboxInput(attrs={'class':_CLASS_CHECK}))
    node_down_grace_pd = PrefixedIntegerField(required=False,
            max_value=_NODE_DOWN_GRACE_PD_MAX,
            min_value=_NODE_DOWN_GRACE_PD_MIN,
            label=_NODE_DOWN_GRACE_PD_LABEL,
            help_text=_NODE_DOWN_GRACE_PD_HELP_TEXT,
            widget=forms.TextInput(attrs={'class':_CLASS_SHORT}))
    
    get_version = forms.BooleanField(required=False,
            label=_GET_VERSION_LABEL,
            widget=forms.CheckboxInput(attrs={'class':_CLASS_CHECK}))
    version_type = forms.ChoiceField(required=False,
            choices=(_VERSION_TYPE_CHOICES),
            widget=forms.RadioSelect(attrs={'class':_CLASS_RADIO}))
    
    get_band_low = forms.BooleanField(required=False,
            label=_GET_BAND_LOW_LABEL,
            widget=forms.CheckboxInput(attrs={'class':_CLASS_CHECK}))
    band_low_threshold = PrefixedIntegerField(required=False, 
            max_value=_BAND_LOW_THRESHOLD_MAX,
            min_value=_BAND_LOW_THRESHOLD_MIN, 
            label=_BAND_LOW_THRESHOLD_LABEL,
            help_text=_BAND_LOW_THRESHOLD_HELP_TEXT,
            widget=forms.TextInput(attrs={'class':_CLASS_SHORT}))
    
    get_t_shirt = forms.BooleanField(required=False,
            label=_GET_T_SHIRT_LABEL,
            widget=forms.CheckboxInput(attrs={'class':_CLASS_CHECK}))

    def __init__(self, data = None, initial = None):
        if data == None:
            if initial == None:
                forms.Form.__init__(self, initial=GenericForm._INIT_MAPPING)
            else:
                forms.Form.__init__(self, initial=initial)
        else:
            forms.Form.__init__(self, data)

        self.version_section_text = GenericForm._VERSION_SECTION_INFO
        self.t_shirt_section_text = GenericForm._T_SHIRT_SECTION_INFO

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
        every time the is_valid method is called on a GenericForm POST 
        request).
                
        @return: The 'cleaned' data from the POST request.
        """
        self.check_if_sub_checked(self.cleaned_data)

        return self.cleaned_data

class SubscribeForm(GenericForm):
    """Inherits from L{GenericForm}. The SubscribeForm class contains
    all the fields in the GenericForm class and additional fields for 
    the user's email and the fingerprint of the router the user wants to
    monitor.
    
    @type _EMAIL_1_LABEL: str
    @cvar _EMAIL_1_LABEL: Text displayed above L{email_1} field.
    @type _EMAIL_MAX_LEN: str
    @cvar _EMAIL_MAX_LEN: Maximum length of L{email_1} field.
    @type _EMAIL_2_LABEL: str
    @type _FINGERPRINT_LABEL: Text displayed above L{email_2} field.
    @type _FINGERPRINT_MAX_LEN:
    @type _SEARCH_LABEL:
    @type _SEARCH_MAX_LEN:
    @type _SEARCH_ID:
    @type _CLASS_EMAIL:
    @type _CLASS_LONG:

    @type email_1:
    @type email_2:
    @type fingerprint:
    @type router_search:

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
    _FINGERPRINT_MAX_LEN = 80
    _SEARCH_LABEL = 'Enter router name, then click the arrow:'
    _SEARCH_MAX_LEN = 80
    _SEARCH_ID = 'router_search'
    _CLASS_EMAIL = 'email-input'
    _CLASS_LONG = 'long-input'

    email_1 = forms.EmailField(label=_EMAIL_1_LABEL,
            widget=forms.TextInput(attrs={'class':_CLASS_EMAIL}),
            max_length=_EMAIL_MAX_LEN)
    email_2 = forms.EmailField(label='Re-enter Email:',
            widget=forms.TextInput(attrs={'class':_CLASS_EMAIL}),
            max_length=_EMAIL_MAX_LEN)
    fingerprint = forms.CharField(label=_FINGERPRINT_LABEL,
            widget=forms.TextInput(attrs={'class':_CLASS_LONG}),
            max_length=_FINGERPRINT_MAX_LEN)
    router_search = forms.CharField(label=_SEARCH_LABEL,
            max_length=_SEARCH_MAX_LEN,
            widget=forms.TextInput(attrs={'id':_SEARCH_ID,                  
                'autocomplete': 'off'}),
            required=False)

    def __init__(self, data = None, initial = None):
        if data == None:
            if initial == None:
                GenericForm.__init__(self)
            else:
                GenericForm.__init__(self, initial=initial)
        else:
            GenericForm.__init__(self, data)

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

        if 'node_down_grace_pd' in self._errors:
            if PrefixedIntegerField.default_error_messages['empty'] in \
                    str(self._errors['node_down_grace_pd']):
               del self._errors['node_down_grace_pd']
               data['node_down_grace_pd'] = \
                       GenericForm._NODE_DOWN_GRACE_PD_INIT

        if 'band_low_threshold' in self._errors:
            if PrefixedIntegerField.default_error_messages['empty'] in \
                    str(self._errors['band_low_threshold']):
                del self._errors['band_low_threshold']
                data['band_low_threshold'] = \
                        GenericForm._BAND_LOW_THRESHOLD_INIT

        return data

    def clean_fingerprint(self):
        """Uses Django's built-in 'clean' form processing functionality to
        test whether the fingerprint entered is a router we have in the
        current database, and presents an appropriate error message if it
        isn't (along with helpful information).

        @rtype: str
        @return: String representation of the entered fingerprint, if it
            is a valid router fingerprint.
        @raise ValidationError: Raises a validation error if no valid 
        """
        fingerprint = self.cleaned_data.get('fingerprint')
        
        # Removes spaces from fingerprint field.
        fingerprint = re.sub(r' ', '', fingerprint)

        if self.is_valid_router(fingerprint):
            return fingerprint
        else:
            info_extension = url_helper.get_fingerprint_info_ext(fingerprint)
            msg = 'We could not locate a Tor node with that fingerprint. \
                   (<a target=_BLANK href=%s>More info</a>)' % info_extension
            raise forms.ValidationError(msg)

    def is_valid_router(self, fingerprint):
        """Helper function to check if a router exists in the database.

        @type fingerprint: str
        @param fingerprint: String representation of a router's fingerprint.
        @rtype: bool
        @return: Whether a router with the specified fingerprint exists in
            the database.
        """

        # The router fingerprint field is unique, so we only need to worry
        # about the router not existing, not there being two routers.
        try:
            Router.objects.get(fingerprint=fingerprint)
        except Router.DoesNotExist:
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
    """The form for changing preferences, as displayed on the preferences 
    page. The form displays the user's current settings for all subscription 
    types (i.e. if they haven't selected a subscription type, the box for that 
    field is unchecked). The PreferencesForm form inherits L{GenericForm}.
    """
    
    _USER_INFO_STR = '<p><span>Email:</span> %s</p> \
            <p><span>Router name:</span> %s</p> \
            <p><span>Router id:</span> %s</p>'

    def __init__(self, user, data = None):
        # If no data, is provided, then create using preferences as initial
        # form data. Otherwise, use provided data.
        if data == None:
            GenericForm.__init__(self, initial=user.get_preferences())
        else:
            GenericForm.__init__(self, data)
 
        self.user = user

        self.user_info = PreferencesForm._USER_INFO_STR % (self.user.email, \
                self.user.router.name, user.router.spaced_fingerprint())

    def change_subscriptions(self, old_data, new_data):
        """Change the subscriptions and options if they are specified.
        
        @type new_data: dict {unicode: various}
        @param new_data: New preferences.
        """

        old_data = self.user.get_preferences()

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
