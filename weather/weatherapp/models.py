"""
The models module handles the bulk of Tor Weather. The module contains three
models that correspond to database tables (L{Subscriber}, L{Subscription}, and 
L{Router}) as well as two form classes (L{SubscribeForm} and
L{PreferencesForm}), which specify the fields to appear on the sign-up
and change preferences pages.
"""
from datetime import datetime
import base64
import os

import emails
from weather.config import url_helper

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
    name = models.CharField(max_length=100)
    welcomed = models.BooleanField(default=False)
    last_seen = models.DateTimeField('date last seen', default=datetime.now())
    up = models.BooleanField(default=True)
    exit = models.BooleanField()

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
    """A subscription class for node-down subscriptions, which send 
    notifications to the user if their node is down for the downtime grace
    period they specify. 

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

    #def should_email():
        #"""
        #"""
        #time_since_changed


class TShirtSub(Subscription):
    """A subscription class for T-shirt notifications. An email is sent
    to the user if the router they're monitoring has earned them a T-shirt.
    The router must be running for 61 days (2 months). If it's an exit node,
    it's avg bandwidth must be at least 100 KB/s. Otherwise, it must be at 
    least 500 KB/s.
    
    @type avg_bandwidth: int
    @ivar avg_bandwidth: The router's average bandwidth
    @type hours_since_triggered: int
    @ivar hours_since_triggered: The hours this router has been up"""
    avg_bandwidth = models.IntegerField()
    hours_since_triggered = models.IntegerField()

    def should_email():
        """Returns true if the router being watched has been up for 1464 hours
        (61 days, or approx 2 months). If it's an exit node, the avg bandwidth
        must be above 100 KB/s. If not, it must be > 500 KB/s.
        
        @rtype: bool
        @return: C{True} if the user earned a T-shirt, C{False} if not."""
        if not emailed and triggered and hours_since_triggered > 1464:
            if subscriber.router.exit:
                if avg_bandwidth > 100000:
                    return True
            else:
                if avg_bandwidth > 500000:
                    return True
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

    def clean_grace_pd(self):
        """Django lets you specify how to 'clean' form data for specific
        fields by adding clean methods to the form classes. The grace 
        period for downtime must be between 1 and 8760, and this method
        ensures that an error message is displayed to the user if they
        try to submit a value outside that range.
        """ 
        grace_pd = self.cleaned_data.get('grace_pd')
        if grace_pd < 1 or grace_pd > 8760:
            raise forms.ValidationError("You must enter a number between " 
                                        + "1 and 8760")
        return grace_pd

    def clean_fingerprint(self):
        """Raises a validation error if the fingerprint the user entered
        wasn't found in the database. The error message contains a link
        to a page listing possible problems.
        """
        fingerprint = self.cleaned_data.get('fingerprint')
        fingerprint.replace(' ','')
        fingerprint_set = Router.objects.filter(fingerprint=fingerprint)
        if len(fingerprint_set) == 0:
            info_ext = url_helper.get_fingerprint_info_ext(fingerprint)
            message = "We could not locate a Tor node with that fingerprint. "+\
                      "(<a href=%s>More info</a>)" % info_ext
            raise forms.ValidationError(message)
        return fingerprint

class NewSubscribeForm(forms.Form):
    """For full feature list. NOWHERE NEAR READY. """

    email_1 = forms.EmailField(max_length=75, help_text='Email:')
    email_2 = forms.EmailField(max_length=75, help_text='Re-enter Email:')
    fingerprint = forms.CharField(max_length=40, help_text='Node Fingerprint:')

    get_node_down = forms.BooleanField(
            help_text='Receive notifications when node is down')
    node_down_grace_pd = forms.IntegerField( 
            help_text='How many hours of downtime before we send'
                      + 'a notification?')
    node_down_grace_pd.help_text_2 = \
            'Enter a value between 1 and 4500 (roughly six months)'
    
    get_out_of_date = forms.BooleanField(
            help_text='Receive notifications when node is out of date')
    out_of_date_threshold = forms.ChoiceField(
            choices=((u'c1', u'out of date lvl 1'),
                     (u'c2', u'out of date lvl 2'),
                     (u'c3', u'out of date lvl 3'),
                     (u'c4', u'out of date lvl 4')),
                help_text='How current would you like your version of Tor?')
    out_of_date_grace_pd = forms.IntegerField(
            help_text='How quickly, in days, would you like to be notified?')
    out_of_date_grace_pd.help_text_2 = \
            'Enter a value between 1 and 200 (roughly six months)'
    
    get_band_low = forms.BooleanField(
            help_text='Receive notifications when node has low bandwidth')
    out_of_date_threshold = forms.IntegerField(
            help_text='Critical bandwidth measured in kilobits')
    out_of_date_grace_pd = forms.IntegerField(
            help_text='How many hours of low bandwidth?')
    out_of_date_grace_pd.help_text_2 = \
            'Enter a value between 1 and 4500 (roughly six months)'

    get_t_shirt = forms.BooleanField(
            help_text='Receive notification when node has earned a t-shirt')
    t_shirt_grace_pd = forms.IntegerField(
            help_text='How quickly, in days, would you like to be notified?')
    t_shirt_grace_pd.help_text_2 = \
            'Enter a value between 1 and 200 (roughly six months)'


class PreferencesForm(forms.Form):
    """The form for changing preferences.

    @ivar grace_pd: A fiend for the user to specify the hours of 
        downtime before an email notification is sent"""

    grace_pd = forms.IntegerField(widget=forms.TextInput(attrs={'size':'25'}))

    def clean_grace_pd(self):
        """Ensures an error message is displayed to the user if they try to
        enter a downtime grace period outside the range of 1-8760 hours."""
        grace_pd = self.cleaned_data.get('grace_pd')
        if grace_pd < 1 or grace_pd > 8760:
            raise forms.ValidationError("You must enter a number between "
                                        + "1 and 8760.")
        return grace_pd

