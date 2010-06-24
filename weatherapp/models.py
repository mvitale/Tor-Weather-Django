"""
The models module handles the bulk of Tor Weather. The module contains three
models that correspond to database tables (L{Subscriber}, L{Subscription}, and 
L{Router}) as well as two form classes (L{SubscribeForm} and
L{PreferencesForm}), which specify the fields to appear on the sign-up
and change preferences pages.
"""

from django.db import models
from django import forms
import emails
from datetime import datetime
import base64
import os

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
    @ivar up: True if this router was up last time a new network consensus
              was published, false otherwise. Default value is C{True}.
    """

    fingerprint = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=100)
    welcomed = models.BooleanField(default=False)
    last_seen = models.DateTimeField('date last seen', default=datetime.now())
    up = models.BooleanField(default=True)

    def __unicode__(self):
        return self.fingerprint


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

    @ivar email: The subscriber's email.
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
    """
    email = models.EmailField(max_length=75)
    router = models.ForeignKey(Router)
    confirmed = models.BooleanField(default = False)
# --------------------- IS THIS OK?? (default = ...) ----------------------
    confirm_auth = models.CharField(max_length=250, 
                    default=SubscriberManager.get_rand_string) 
    unsubs_auth = models.CharField(max_length=250, 
                    default=SubscriberManager.get_rand_string)
    pref_auth = models.CharField(max_length=250, 
                    default=SubscriberManager.get_rand_string)

    sub_date = models.DateTimeField(default=datetime.now())

    objects = SubscriberManager()

    def __unicode__(self):
        return self.email


class SubscriptionManager(models.Manager):
    """The custom Manager for the Subscription class. The Manager contains
    a method to get the number of hours since the time stored in the
    'last_changed' field in a Subscription object.
    """

    @staticmethod
    def get_hours_since_changed(last_changed):
        """Returns the time that has passed since the datetime parameter
        last_changed in hours.

        @type last_changed: datetime.datetime
        @param last_changed: The date and time of the most recent change
            for some flag.
        @rtype: int
        @return: The number of hours since last_changed.
        """
        time_since_changed = datetime.now() - last_changed
        hours_since_changed = time_since_changed.seconds / 3600
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
    @type triggered: bool
    @ivar triggered: True if the threshold has been passed for this 
        subscription/the conditions to send a notification are met, False
        if not. Default upon creation is C{False}.
    @type last_changed: datetime.datetime
    @ivar last_changed: The most recent datetime when the trigger field 
        was changed. Default upon creation is C{datetime.now()}.
    """
    subscriber = models.ForeignKey(Subscriber)
    emailed = models.BooleanField(default=False)
    triggered = models.BooleanField(default=False)
    last_changed = models.DateTimeField('date of last change', 
                                        default=datetime.now())

    # In Django, Manager objects handle table-wide methods (i.e filtering)
    objects = SubscriptionManager()
    
    def __unicode__(self):
        return self.subscriber.email


class NodeDownSub(Subscription):
    """

    @type grace_pd: int
    @ivar grace_pd: The amount of time (hours) before a notification is sent
        after a node is seen down.
    """
    grace_pd = models.IntegerField()

    def should_email():
        """Returns a bool representing whether or not the Subscriber should
        be emailed about their node being down.

        @rtype: bool
        @return: True if the Subscriber should be emailed because their node
            is down and the grace period has passed, False otherwise.
        """
        hours_since_changed = \
            SubscriptionManager.get_hours_since_changed(last_changed)
        if triggered and not emailed and \
                     (hours_since_changed > grace_pd):
            return True
        else:
            return False

class VersionSub(Subscription):
    """

    @type threshold: str
    @ivar threshold: The threshold for sending a notification (i.e. send a 
        notification if the version is obsolete vs. out of date)
    """
# -----------------------------------------------------------------------
# FILL IN LATER, FIX DOCUMENTATION
# -----------------------------------------------------------------------
    threshold = models.CharField(max_length=250)

    def should_email():
        """
        """


class LowBandwidthSub(Subscription):    
    """
    """
    threshold = models.IntegerField(default = 0)
    grace_pd = models.IntegerField(default = 1)

    def should_email():
        """
        """
        time_since_changed


class NewSubscribeForm(forms.Form):
    """For full feature list. """

    _MAX_NODE_DOWN_GRACE_PD = 4500
    _MIN_NODE_DOWN_GRACE_PD = 1
    _MAX_OUT_OF_DATE_GRACE_PD = 200
    _MIN_OUT_OF_DATE_GRACE_PD = 1
    _MAX_BAND_LOW_THRESHOLD = 5000
    _MIN_BAND_LOW_THRESHOLD = 1
    _MAX_BAND_LOW_GRACE_PD = 4500
    _MIN_BAND_LOW_GRACE_PD = 1

    email_1 = forms.EmailField(max_length=75, help_text='Email:')
    email_2 = forms.EmailField(max_length=75, help_text='Re-enter Email:')
    fingerprint = forms.CharField(max_length=40, help_text='Node Fingerprint:')

    get_node_down = forms.BooleanField(
            help_text='Receive notifications when node is down')
    node_down_grace_pd = forms.IntegerField(
            max_value=_MAX_NODE_DOWN_GRACE_PD,
            min_value=_MIN_NODE_DOWN_GRACE_PD,
            help_text='How many hours of downtime before \
                       we send a notifcation?')
    
    get_out_of_date = forms.BooleanField(
            help_text='Receive notifications when node is out of date')
    out_of_date_threshold = forms.ChoiceField(
            choices=((u'c1', u'out of date lvl 1'),
                     (u'c2', u'out of date lvl 2'),
                     (u'c3', u'out of date lvl 3'),
                     (u'c4', u'out of date lvl 4')),
                help_text='How current would you like your version of Tor?')
    out_of_date_grace_pd = forms.IntegerField(
            max_value=_MAX_OUT_OF_DATE_GRACE_PD,
            min_value=_MIN_OUT_OF_DATE_GRACE_PD, 
            help_text='How quickly, in days, would you like to be notified?')
    
    get_band_low = forms.BooleanField(
            help_text='Receive notifications when node has low bandwidth')
    band_low_threshold = forms.IntegerField(
            max_value=_MAX_BAND_LOW_THRESHOLD,
            min_value=_MIN_BAND_LOW_THRESHOLD,
            help_text='Critical bandwidth measured in kilobits per second:')
    band_low_grace_pd = forms.IntegerField(
            max_value=_MAX_BAND_LOW_GRACE_PD,
            min_value=_MIN_BAND_LOW_GRACE_PD,
            help_text='How many hours of low bandwidth before \
                       we send a notification?')
    
    get_t_shirt = forms.BooleanField(
            help_text='Receive notification when node has earned a t-shirt')

class PreferencesForm(forms.Form):
    """For full feature list."""

    _MAX_NODE_DOWN_GRACE_PD = 4500
    _MIN_NODE_DOWN_GRACE_PD = 1
    _MAX_OUT_OF_DATE_GRACE_PD = 200
    _MIN_OUT_OF_DATE_GRACE_PD = 1
    _MAX_BAND_LOW_THRESHOLD = 5000
    _MIN_BAND_LOW_THRESHOLD = 1
    _MAX_BAND_LOW_GRACE_PD = 4500
    _MIN_BAND_LOW_GRACE_PD = 1

    get_node_down = forms.BooleanField(
            help_text='Receive notifications when node is down')
    node_down_grace_pd = forms.IntegerField(
            max_value=_MAX_NODE_DOWN_GRACE_PD,
            min_value=_MIN_NODE_DOWN_GRACE_PD,
            help_text='How many hours of downtime before \
                       we send a notifcation?')
    
    get_out_of_date = forms.BooleanField(
            help_text='Receive notifications when node is out of date')
    out_of_date_threshold = forms.ChoiceField(
            choices=((u'c1', u'out of date lvl 1'),
                     (u'c2', u'out of date lvl 2'),
                     (u'c3', u'out of date lvl 3'),
                     (u'c4', u'out of date lvl 4')),
                help_text='How current would you like your version of Tor?')
    out_of_date_grace_pd = forms.IntegerField(
            max_value=_MAX_OUT_OF_DATE_GRACE_PD,
            min_value=_MIN_OUT_OF_DATE_GRACE_PD, 
            help_text='How quickly, in days, would you like to be notified?')
    
    get_band_low = forms.BooleanField(
            help_text='Receive notifications when node has low bandwidth')
    band_low_threshold = forms.IntegerField(
            max_value=_MAX_BAND_LOW_THRESHOLD,
            min_value=_MIN_BAND_LOW_THRESHOLD,
            help_text='Critical bandwidth measured in kilobits per second:')
    band_low_grace_pd = forms.IntegerField(
            max_value=_MAX_BAND_LOW_GRACE_PD,
            min_value=_MIN_BAND_LOW_GRACE_PD,
            help_text='How many hours of low bandwidth before \
                       we send a notification?')
    
    get_t_shirt = forms.BooleanField(
            help_text='Receive notification when node has earned a t-shirt')
