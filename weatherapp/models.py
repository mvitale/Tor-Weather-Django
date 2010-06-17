"""
The models module handles the bulk of Tor Weather. The module contains three
models that correspond to database tables (L{Subscriber}, L{Subscription}, and 
L{Router}) as well as two form classes (L{SubscribeForm} and
L{PreferencesForm}), which specify the fields to appear on the sign-up
and change preferences pages.
"""

from django.db import models
from django import forms
from weatherapp.helpers import StringGenerator 
from weatherapp.helpers import Emailer
from datetime import datetime
import base64

class RouterManager(models.Manager):
    _WELCOMED_DEFAULT = False

    def add_default_router(self, fingerprint, name,
                           welcomed = None,
                           last_seen = None):
        if welcomed == None:
            welcomed = _WELCOMED_DEFAULT
        if last_seen == None:
            last_seen = datetime.now()

        routr = Router(fingerprint = fingerprint, name = name,
                       welcomed = welcomed, last_seen = last_seen)
        routr.save()
        return routr

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
    up = models.BooleanField()

    objects = RouterManager()
    
    def __unicode__(self):
        return self.fingerprint

    def update(self, 
               fingerprint = None,
               name = None,
               welcomed = None,
               last_seen = None,
               up = None)
        if fingerprint != None:
            self.fingerprint = fingerprint
        if name != None:
            self.name = name
        if welcomed != None:
            self.welcomed = welcomed
        if last_seen != None:
            self.last_seen = last_seen
        if up != None:
            self.up = up

        self.save()
        return self

class SubscriberManager(models.Manager):
    _CONFIRMED_DEFAULT = False

    def add_default_subscriber(self, email, router_id,
                               confirmed = None,
                               confirm_auth = None,
                               unsubs_auth = None,
                               pref_auth = None,
                               sub_date = None):
        if confirmed == None:
            confirmed = _CONFIRMED_DEFAULT

        if confirm_auth == None:
            confirm_auth = get_rand_string()
        if unsubs_auth == None:
            unsubs_auth = get_rand_string()
        if pref_auth == None:
            pref_auth = get_rand_string()

        if sub_date == None:
            sub_date = datetime.now()

        subr = Subscriber(email = email, router = router_id,
                          confirmed = confirmed, confirm_auth = confirm_auth,
                          unsubs_auth = unsubs_auth, pref_auth = pref_auth)
        subr.save()
        return subr

    def get_query_set(self):
        return super(SubscriberManager, self).get_query_set()

    def get_rand_string(length = 24):
        """Gets a random string with length length.

        @type length: int
        @param length: The length of the random string. Max is 24. If length
        > 24, the random string returned will have length 24."""

        cut_off = length - 24
        if cut_off <= 0:
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

    objects = SubscriberManager()

    def __unicode__(self):
        return self.email

    def update(self,
               email = None,
               router = None,
               confirmed = None,
               confirm_auth = None,
               unsubs_auth = None,
               pref_auth = None,
               sub_date = None):
        if email != None:
            self.email = email
        if router != None:
            self.router = router
        if confirmed != None:
            self.confirmed = confirmed
        if confirm_auth != None:
            self.confirm_auth = confirm_auth
        if unsubs_auth != None:
            self.unsubs_auth = unsubs_auth
        if pref_auth != None:
            self.pref_auth = pref_auth
        if sub_date != None:
            self.sub_date = sub_date

        self.save()
        return self

class SubscriptionManager(models.Manager):
    _EMAILED_DEFAULT = False
    _TRIGGERED_DEFAULT = False

    def add_default_subscription(self, subscriber_id, name, threshold, 
                                 grace_pd,
                                 emailed = None,
                                 triggered = None,
                                 last_changed = None):
        if emailed == None:
            emailed = _EMAILED_DEFAULT
        if triggered == None,
            triggered = _TRIGGERED_DEFAULT
        if last_changed == None,
            last_changed = datetime.now()
            
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

    def update(self,
               subscriber = None,
               name = None,
               threshold = None,
               grace_pd = None,
               emailed = None,
               triggered = None,
               last_changed = None):
        if subscriber == None:
            self.subscriber = subscriber
        if name == None:
            self.name = name
        if threshold == None:
            self.threshold = threshold
        if grace_pd == None:
            self.grace_pd = grace_pd
        if emailed == None:
            self.emailed = emailed
        if triggered = None:
            self.triggered = triggered
        if last_changed = None:
            self.last_changed = last_changed

        self.save()
        return self

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
