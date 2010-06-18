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

class RouterManager(models.Manager):
    def get_query_set(self):
        return super(RouterManager, self).get_query_set()

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

    objects = RouterManager()
    
    def __unicode__(self):
        return self.fingerprint

class SubscriberManager(models.Manager):
    def get_query_set(self):
        return super(SubscriberManager, self).get_query_set()

    @staticmethod
    def get_rand_string(length = 24):
        cut_off = length - 24
        if cut_off == 0:
            cut_off = 24

        r = base64.urlsafe_b64encode(os.urandom(18))[:cut_off]

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

    confirm_auth = models.CharField(max_length=250, 
                    default=SubscriberManager.get_rand_string()) 
    unsubs_auth = models.CharField(max_length=250, 
                    default=SubscriberManager.get_rand_string())
    pref_auth = models.CharField(max_length=250, 
                    default=SubscriberManager.get_rand_string())

    sub_date = models.DateTimeField(default=datetime.now())

    objects = SubscriberManager()

    def __unicode__(self):
        return self.email

class SubscriptionManager(models.Manager):
    def get_query_set(self):
        return super(SubscriptionManager, self).get_query_set()
    
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
    name = models.CharField(max_length=200)
    threshold = models.CharField(max_length=200)
    grace_pd = models.IntegerField()
    emailed = models.BooleanField(default=False)
    triggered = models.BooleanField(default=False)
    last_changed = models.DateTimeField('date of last change', 
                                        default=datetime.now())

    objects = SubscriptionManager()
    
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

class NewSubscribeForm(forms.Form):
    """For full feature list. NOWHERE NEAR READY. """

    email_1 = forms.EmailField(max_length=75, help_text='Email:')
    email_2 = forms.EmailField(max_length=75, help_text='Re-enter Email:')
    fingerprint = forms.CharField(max_length=40, help_text='Node Fingerprint:')

    get_node_down = forms.BooleanField(
            help_text='Receive notifications when node is down')
    node_down_grace_pd = forms.IntegerField(max_length=4, 
            help_text='How many hours of downtime?')
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
    out_of_date_grace_pd = forms.IntegerField(max_length=4,
            help_text='How quickly, in days, would you like to be notified?')
    out_of_date_grace_pd.help_text_2 = \
            'Enter a value between 1 and 200 (roughly six months)'
    
    get_band_low = forms.BooleanField(
            help_text='Receive notifications when node has low bandwidth')
    out_of_date_threshold = forms.IntegerField(max_length=10,
            help_text='Critical bandwidth measured in kilobits')
    out_of_date_grace_pd = forms.IntegerField(max_lenght=4,
            help_text='How many hours of low bandwidth?')
    out_of_date_grace_pd.help_text_2 = \
            'Enter a value between 1 and 4500 (roughly six months)'

    get_t_shirt = forms.BooleanField(
            help_text='Receive notification when node has earned a t-shirt')
    t_shirt_grace_pd = forms.IntegerField(max_length=4,
            help_text='How quickly, in days, would you like to be notified?')
    t_shirt_grace_pd.help_text_2 = \
            'Enter a value between 1 and 200 (roughly six months)'

class PreferencesForm(forms.Form):
    """The form for changing preferences.

    @ivar grace_pd: A fiend for the user to specify the hours of 
        downtime before an email notification is sent"""

    grace_pd = forms.IntegerField(widget=forms.TextInput(attrs={'size':'50'}))
