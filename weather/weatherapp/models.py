"""
The models module handles the bulk of Tor Weather's database management. The
module contains three models that correspond to the three main database tables
(L{Router}, L{Subscriber}, and L{Subscription}), as well as four subclasses of
L{Subscription} for the various subscription types and three classes for forms
(L{GenericForm}, L{SubscribeForm}, and L{PreferencesForm}), which specify and do
the work of the forms displayed on the sign-up and preferences pages.

@group Helper Functions: insert_fingerprint_spaces, get_rand_string,
    hours_since
@group Models: Router, Subscriber, Subscription
@group Subscription Subclasses: NodeDownSub, VersionSub, BandwidthSub, 
    TShirtSub
@group Forms: GenericForm, SubscribeForm, PreferencesForm
@group Custom Fields: PrefixedIntegerField
"""

from datetime import datetime
import base64
import os
import re
from copy import copy

from config import url_helper

from django.db import models
from django import forms
from django.forms import ValidationError


# HELPER FUNCTIONS ------------------------------------------------------------
# ----------------------------------------------------------------------------- 

def insert_fingerprint_spaces(fingerprint):
    """Insert a space into C{fingerprint} every four characters.

    @type fingerprint: str
    @arg fingerprint: A router L{fingerprint<Router.fingerprint>}

    @rtype: str
    @return: a L{fingerprint<Router.fingerprint>} with spaces inserted every 
    four characters.
    """

    return ' '.join(re.findall('.{4}', str(fingerprint)))

def get_rand_string():
    """Returns a random, url-safe string of 24 characters (no '+' or '/'
    characters). The generated string does not end in '-'. Main purpose is
    for authorization URL extensions.
        
    @rtype: str
    @return: A randomly generated, 24 character string (url-safe).
    """

    r = base64.urlsafe_b64encode(os.urandom(18))

    # some email clients don't like URLs ending in -
    if r.endswith("-"):
        r = r.replace("-", "x")
    return r  

def hours_since(time):
    """Get the number of hours passed since datetime C{time}.

    @type time: C{datetime}
    @arg time: A C{datetime} object.
    @rtype: int
    @return: The number of hours since C{time}.
    """
    
    delta = datetime.now() - time
    hours = (delta.days * 24) + (delta.seconds / 3600)
    return hours


# MODELS ----------------------------------------------------------------------
# -----------------------------------------------------------------------------

class Router(models.Model):
    """Model for Tor network routers. 
    Django uses class variables to specify model fields, but these fields are
    practically used and thought of as instance variables, so this 
    documentation will refer to them as such. Field types are specified as
    their Django field classes, with parentheses indicating the python type
    they are validated against and are treated as practically. When 
    constructing a L{Router} object, instance variables are specified as 
    keyword arguments in L{Router} constructors.
   
    @type _FINGERPRINT_MAX_LEN: int
    @cvar _FINGERPRINT_MAX_LEN: Maximum valid length for L{fingerprint}
        fields.
    @type _NAME_MAX_LEN: int
    @cvar _NAME_MAX_LEN: Maximum valid length for L{name} fields.
    @type _DEFAULTS: dict {str: various}
    @cvar _DEFAULTS: Dictionary mapping field names to their default
        parameters. These are the values that fields will be instantiated with
        if they are not specified in the model's construction.

    @type fingerprint: CharField (str)
    @ivar fingerprint: The L{Router}'s fingerprint. Required constructor
        argument.
    @type name: CharField (str)
    @ivar name: The L{Router}'s name. Default value is C{'Unnamed'}.
    @type welcomed: BooleanField (bool)
    @ivar welcomed: Whether the L{Router} operator has received a welcome
        email. Default value is C{False}.
    @type last_seen: DateTimeField (datetime)
    @ivar last_seen: The most recent time the L{Router} was seen in consensus.
        Default value is a call to C{datetime.now()}.
    @type up: BooleanField (bool)
    @ivar up: Whether this L{Router} was up the last time a new consensus
        document was published. Default value is C{True}.
    @type exit: BooleanField (bool)
    @ivar exit: Whether this L{Router} is an exit node (if it accepts exits 
        to port 80). Default is C{False}.
    """
    
    _FINGERPRINT_MAX_LEN = 40
    _NAME_MAX_LEN = 100
    _DEFAULTS = { 'name': 'Unnamed',
                  'welcomed': False,
                  'last_seen': datetime.now,
                  'up': True,
                  'exit': False }

    fingerprint = models.CharField(max_length=_FINGERPRINT_MAX_LEN,
            default=None, blank=False)
    name = models.CharField(max_length=_NAME_MAX_LEN,
            default=_DEFAULTS['name'])
    welcomed = models.BooleanField(default=_DEFAULTS['welcomed'])
    last_seen = models.DateTimeField(default=_DEFAULTS['last_seen'])
    up = models.BooleanField(default=_DEFAULTS['up'])
    exit = models.BooleanField(default=_DEFAULTS['exit'])

    def __unicode__(self):
        """Returns a simple description of this L{Router}, namely its L{name}
        and L{fingerprint}.
        
        @rtype: str
        @return: Simple description of L{Router} object.
        """

        return self.name + ": " + self.spaced_fingerprint()

    def spaced_fingerprint(self):
        """Returns the L{fingerprint} for this L{Router} as a string with
        spaces inserted every 4 characters.
        
        @rtype: str
        @return: The L{Router}'s L{fingerprint} with spaces inserted.
        """

        return insert_fingerprint_spaces(self.fingerprint)

class Subscriber(models.Model):
    """Model for Tor Weather subscribers. 

    Django uses class variables to specify model fields, but these fields are 
    practically used and thought of as instance variables, so this 
    documentation will refer to them as such. Field types are specified as 
    their Django field classes, with parentheses indicating the python type 
    they are validated against and treated as practically. When constructing a 
    L{Subscriber} object, instance variables are specified as keyword arguments
    in L{Subscriber} constructors.

    @type _EMAIL_MAX_LEN: int
    @cvar _EMAIL_MAX_LEN: Maximum length for L{email} field.
    @type _AUTH_MAX_LEN: int
    @cvar _AUTH_MAX_LEN: Maximum length for L{confirm_auth}, L{unsubs_auth},
        L{pref_auth}
    @type _DEFAULTS: Dictionary
    @cvar _DEFAULTS: Dictionary mapping field names to their default
        parameters. These are the values that fields will be instantiated with
        if they are not specified in the model's construction.

    @type email: EmailField (str)
    @ivar email: The L{Subscriber}'s email address. Required constructor 
        argument.
    @type router: L{Router}
    @ivar router: The L{Router} the L{Subscriber} is subscribed to. Required
        constructor argument.
    @type confirmed: BooleanField (bool)
    @ivar confirmed: Whether the user has confirmed their subscription through
        an email confirmation link; C{True} if they have, C{False} if they 
        haven't. Default value is C{False}.
    @type confirm_auth: CharField (str)
    @ivar confirm_auth: Confirmation authorization code. Default value is a
        random string generated by L{get_rand_string}.
    @type unsubs_auth: CharField (str)
    @ivar unsubs_auth: Unsubscription authorization code. Default value is a
        random string generated by L{get_rand_string}.
    @type pref_auth: CharField (str)
    @ivar pref_auth: Preferences access authorization code. Default value is a
        random string generated by L{get_rand_string}.
    @type sub_date: DateTimeField (datetime)
    @ivar sub_date: Datetime at which the L{Subscriber} subscribed. Default 
        value is the current time, evaluated by a call to C{datetime.now}.
    """

    _EMAIL_MAX_LEN = 75
    _AUTH_MAX_LEN = 25
    _DEFAULTS = { 'confirmed': False,
                  'confirm_auth': get_rand_string,
                  'unsubs_auth': get_rand_string,
                  'pref_auth': get_rand_string,
                  'sub_date': datetime.now }

    email = models.EmailField(max_length=_EMAIL_MAX_LEN, 
            default=None, blank=False)
    router = models.ForeignKey(Router, default=None, blank=False)
    confirmed = models.BooleanField(default=_DEFAULTS['confirmed'])
    confirm_auth = models.CharField(max_length=_AUTH_MAX_LEN,
            default=_DEFAULTS['confirm_auth'])
    unsubs_auth = models.CharField(max_length=_AUTH_MAX_LEN,
            default=_DEFAULTS['unsubs_auth'])
    pref_auth = models.CharField(max_length=_AUTH_MAX_LEN,
            default=_DEFAULTS['pref_auth'])
    sub_date = models.DateTimeField(default=_DEFAULTS['sub_date'])

    def __unicode__(self):
        """Returns a simple description of this L{Subscriber}, namely
        its L{email}.
        
        @rtype: str
        @return: Simple description of L{Subscriber}.
        """
        return self.email
 
    def _has_sub_type(self, sub_type):
        """Checks if this L{Subscriber} has a L{Subscription} of type
        C{sub_type}.

        @type sub_type: str
        @arg sub_type: The type of L{Subscription} to check. This must be the 
            exact name of a subclass of L{Subscription} (L{NodeDownSub},
            L{VersionSub}, L{BandwidthSub}, or L{TShirtSub}).
        @rtype: bool
        @return: Whether this L{Subscriber} has a L{Subscription} of type
            C{sub_type}; C{True} if it does, C{False} if it doesn't. Also 
            returns C{False} if C{sub_type} is not a valid name of a 
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
        except Exception, e:
            raise e
        else:
            return True

    def has_node_down_sub(self):
        """Checks if this L{Subscriber} has a L{NodeDownSub}.

        @rtype: bool
        @return: Whether a L{NodeDownSub} exists for this L{Subscriber}; C{True}
            if it does, C{False} if it doesn't.
        """
        
        return self._has_sub_type('NodeDownSub')

    def has_version_sub(self):
        """Checks if this L{Subscriber} has a L{VersionSub}.
        
        @rtype: bool
        @return: Whether a L{VersionSub} exists for this L{Subscriber}; C{True}
            if it does, C{False} if it doesn't.
        """

        return self._has_sub_type('VersionSub')

    def has_bandwidth_sub(self):
        """Checks if this L{Subscriber} has a L{BandwidthSub}.

        @rtype: bool
        @return: Whether a L{BandwidthSub} exists for this L{Subscriber};
            C{True} if it does, C{False} if it doesn't.

        """

        return self._has_sub_type('BandwidthSub')

    def has_t_shirt_sub(self):
        """Checks if this L{Subscriber} has a L{TShirtSub}.
        
        @rtype: bool
        @return: Whether a L{TShirtSub} exists for this L{Subscriber}; C{True}
            if it does, C{False} if it doesn't.
        """

        return self._has_sub_type('TShirtSub')

    def determine_unit(self, hours):
        """Determines the time unit entered for the node_down_grace_pd.
        The unit entered in the form isn't saved internally, and everything is
        converted to hours, so this method checks to see if the number of hours
        stored is expressable as a whole number of months, weeks, or days.

        @type hours: int
        @arg hours: A number of hours.
        @rtype: str
        @return: C{H} (hours), C{D} (days), C{W} (weeks), or C{M} (months).
            Longer time periods take precedence, so if an input is an even
            number of days and months (as it necessarily has to be to be an
            even number of months), then C{M} will be returned, not C{D}.
        """
        
        if hours % (24 * 30) == 0:
            return 'M'
        elif hours % (24 * 7) == 0:
            return 'W'
        elif hours % (24) == 0:
            return 'D'
        else:
            return 'H'

    def get_preferences(self):
        """Compiles a dictionary of preferences for this L{Subscriber}.
        Key names are the names of fields in L{GenericForm}, L{SubscribeForm},
        and L{PreferencesForm}. This is mainly to be used to determine a user's
        current preferences in order to generate an initial preferences page.
        Checks the database for L{Subscription}s corresponding to the
        L{Subscriber}, and returns a dictionary with the settings of all
        L{Subscription}s found. The dictionary does not contain entries for 
        fields of L{Subscription}s not subscribed to (except for the
        L{GenericForm.get_node_down}, C{GenericForm.get_version}, 
        C{GenericForm.get_band_low}, and C{GenericForm.get_t_shirt}
        fields, which will be C{False} if a L{Subscription} doesn't exist).

        @rtype: Dict {str: various}
        @return: Dictionary of current preferences for this L{Subscriber}.
        """
        
        data = {}

        data['get_node_down'] = self.has_node_down_sub()
        if data['get_node_down']:
            n = NodeDownSub.objects.get(subscriber = self)
            unit = self.determine_unit(n.grace_pd)
            data['node_down_grace_pd_unit'] = unit
            if unit == 'M':
                grace_pd = n.grace_pd / (24 * 30)
            elif unit == 'W':
                grace_pd = n.grace_pd / (24 * 7)
            elif unit == 'D':
                grace_pd = n.grace_pd / (24)
            else: 
                grace_pd = n.grace_pd
            data['node_down_grace_pd'] = grace_pd
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

class Subscription(models.Model):
    """Generic (abstract) model for Tor Weather subscriptions. Only contains
    fields which are used by all types of Tor Weathe Dictionary subscriptions.

    Django uses class variables to specify model fields, but these fields are
    practically used and thought of as instance variables, so this 
    documentation will refer to them as such. Field types are specified as 
    their Django field classes, with parentheses indicating the python type 
    they are validated against and treated as practically. When constructing
    a L{Subscription} object, instance variables are specified as keyword
    arguments in L{Subscription} constructors.

    @type _DEFAULTS: dict {str: various}
    @cvar _DEFAULTS: Dictionary mapping field names to their default
        parameters. These are the values that fields will be instantiated
        with if they are not specified in the model's construction.

    @type subscriber: L{Subscriber}
    @ivar subscriber: The L{Subscriber} who is subscribed to this
        L{Subscription}. Required constructor argument.
    @type emailed: BooleanField (bool)
    @ivar emailed: Whether the user has already been emailed about this
        L{Subscription} since it has been triggered; C{True} if they have
        been, C{False} if they haven't been. Default value is C{False}.
    """

    _DEFAULTS = { 'emailed': False }

    subscriber = models.ForeignKey(Subscriber, default=None, blank=False)
    emailed = models.BooleanField(default=_DEFAULTS['emailed'])


# SUBSCRIPTION SUBCLASSES -----------------------------------------------------
# -----------------------------------------------------------------------------

class NodeDownSub(Subscription):
    """Model for node-down notification subscriptions, which send notifications
    to their C{susbcriber} if the C{subscriber}'s C{router} is offline for
    C{grace_pd} hours.
    Django uses class variables to specify model fields, but these fields are
    practically used and thought of as instance variables, so this
    documentation will refer to them as such. Fields are specfieid as their 
    Django field classes, with parentheses indicating the python type they are
    validated against and treated as practically.

    @type _DEFAULTS: dict {str: various}
    @cvar _DEFAULTS: Dictionary mapping field names to their default
        parameters. These are the values that fields will be instantiated
        with if they are not specified in the model's construction.

    @type triggered: BooleanField (bool)
    @ivar triggered: Whether the C{subscriber}'s C{router} is offline; C{True}
        if it is, C{False} if it isn't. Default value is C{False}.
    @type grace_pd: IntegerField (int)
    @ivar grace_pd: Number of hours which the C{subscriber}'s C{router} must
        be offline before a notification is sent. Required constructor 
        argument.
    @type last_changed: DateTimeField (datetime)
    @ivar last_changed: Datetime at which the L{triggered} flag was last 
        changed. Default value is the current time, evaluated with a call to
        C{datetime.now}.
    """
    
    _DEFAULTS = { 'triggered': False,
                  'last_changed': datetime.now }

    triggered= models.BooleanField(default=_DEFAULTS['triggered'])
    grace_pd = models.IntegerField(default=None, blank=False)
    last_changed = models.DateTimeField(default=_DEFAULTS['last_changed'])
    
    def is_grace_passed(self):
        """Check if the C{subscriber}'s C{router} has been offline for 
        C{grace_pd} hours.
        
        @rtype: bool
        @return: Whether the C{subscriber}'s C{router} has been offline for
            L{grace_pd} hours; C{True} if it has, C{False} if it hasn't.
        """

        if self.triggered \
                and hours_since(self.last_changed) >= grace_pd:
            return True
        else:
            return False

class VersionSub(Subscription):
    """Model for version update notification subscriptions, which send 
    notifications to their C{subscriber} if the C{subscriber}'s C{router} is
    running a version of Tor that is out-of-date. OBSOLETE notifications are
    triggered if the C{router}'s version of Tor is not in the list of 
    recommended versions (obtained via TorCtl), and UNRECOMMENDED notifications
    are triggered if the C{router}'s version fo Tor is not the most recent 
    stable (non-alpha/beta) version of Tor in the list of recommended versions.
    Django uses class variables to specify model fields, but these fields
    are practically used and thought of as instance variables, so this
    documentation will refer to them as such. Field types are specified as 
    their Django field classes, with parentheses indicating the python type 
    they are validated against and treated as practically.

    @type _NOTIFY_TYPE_MAX_LEN: int
    @cvar _NOTIFY_TYPE_MAX_LEN: Maximum length for L{notify_type} field.
    
    @type notify_type: CharField (str)
    @ivar notify_type: The type of notification, either 'UNRECOMMENDED' or 
        'OBSOLETE'. Required constructor argument.
    """

    _NOTIFY_TYPE_MAX_LEN = 13

    notify_type = models.CharField(max_length=_NOTIFY_TYPE_MAX_LEN,
            default=None, blank=False)

class BandwidthSub(Subscription):   
    """Model for low bandwidth notification subscriptions, which send
    notifications to their C{subscriber} if the C{subscriber}'s C{router} has
    an observed bandwidth below their specified C{threshold}. Observer
    bandwidth information is found in descriptor files, and, according to
    the directory specifications, the observed bandwidth field "is an estimate
    of the capacity this server can hadnle. The server remembers the max 
    bandwidth sustained output over any ten second period in the past day,
    and anothe rsustained input. The 'observed' value is the lesser of these
    two numbers."
    Django uses class variables to specify model fields, but these fields are
    practically used and thought of as instance variables, so this
    documentation will refer to them as such. Field types are specified as
    their Django field classes, with parentheses indicating the python type
    they are validated against and treated as practically.

    @type _DEFAULTS: dict {str: various}
    @cvar _DEFAULTS: Dictionary mapping field names to their default
        parameters. These are the values that fields will be instantiated with
        if they are not specified in the model's construction.

    @type threshold: IntegerField (int)
    @ivar threshold: The bandwidth threshold (in kB/s). Default value is 20.
    """

    _DEFAULTS = { 'threshold': 20 }

    threshold = models.IntegerField(_DEFAULTS['threshold'])
    
class TShirtSub(Subscription):
    """Model for t-shirt notification subscriptions, which send notifications 
    to their C{susbcriber} if running their C{router} has earned the 
    C{subscriber} a t-shirt. The (vague) specification for earning a t-shirt by
    running a router is that the router must be running for 61 days (2 months),
    with an average bandwidth of at least 500 kB/s (or 100 kB/s if it's an exit
    node).

    Django uses class variables to specify model fields, but these fields are
    practically used and thought of as instance variables, so this documentation
    will refer to them as such. Field types are specified as their Django field
    classes, with parentheses indicating the pythn type they are validated
    against and are treated as practically. When constructing a L{TShirtSub}
    object, instance variables are specified as keyword arguments in
    L{TShirtSub} constructors.

    @type _DEFAULTS: C{dict} {C{str}: various}
    @cvar _DEFAULTS: Dictionary mapping field names to their default parameters.
        These are the values that fields will be instantiated with if they are
        not specified in the model's construction.

    @type triggered: BooleanField (bool)
    @ivar triggered: Whether the C{router} is up. Default is C{False}.
    @type avg_bandwidth: IntegerField (int)
    @ivar avg_bandwidth: The L{router<Subscriber.router>}'s average bandwidth 
        in kB/s. Default is 0.
    @type last_changed: datetime
    @ivar last_changed: The datetime at which the L{triggered} flag was last
        changed. Default is the current time, evaluated with a call to
        datetime.now.
    """
    
    _DEFAULTS = { 'triggered': False,
                  'avg_bandwidth': 0,
                  'last_changed': datetime.now }

    triggered = models.BooleanField(default=_DEFAULTS['triggered'])
    avg_bandwidth = models.IntegerField(default=_DEFAULTS['avg_bandwidth'])
    last_changed = models.DateTimeField(default=_DEFAULTS['last_changed'])

    def get_hours_since_triggered(self):
        """Get the number of hours that the L{router<Subscriber.router>} has
        been up.

        @rtype: C{bool}
        @return: The number of hours that the router has been up, or C{0} if the
            router is offline.
        """

        if self.triggered == False:
            return 0
        else:
            return hours_since(self.last_changed)
        
    def should_email(self):
        """Determines if the L{subscriber<Subscription.subscriber>} has earned a
        t-shirt by running its L{router<Subscriber.router>}. Determines this by
        checking if the L{router<Subscriber.router>} has been up for 1464 hours
        (61 days, appox 2 months) and then checking if its average bandwidth is
        above the required threshold (100 kB/s for an exit node, 500 kB/s for a
        non-exit node).
        
        @rtype: C{bool}
        @return: Whether the L{subscriber<Subscription.subscriber>} has earned 
            a t-shirt; C{True} if they have, C{False} if they haven't.
        """ 
        
        hours_up = self.get_hours_since_triggered()
        
        if not self.emailed and self.triggered and hours_up >= 1464:
            if self.subscriber.router.exit:
                if self.avg_bandwidth >= 100:
                    return True
            else:
                if self.avg_bandwidth >= 500:
                    return True
        return False


# CUSTOM FIELDS ---------------------------------------------------------------
# -----------------------------------------------------------------------------

class PrefixedIntegerField(forms.IntegerField):
    """An C{IntegerField} that accepts input of the form C{PREFIX INTEGER}
    and parses it as simply C{INTEGER} in its L{to_python} method. A 
    L{PrefixedIntegerField} will not accept empty input, but will throw a
    C{ValidationError} specifying that it was left empty, so that this error 
    can be intercepted and dealth with cleanly. This class does not handle
    displaying the field to include the C{PREFIX}, but simply handles the
    gritty details of validating a field whose data is int but displays text as
    well.

    @type _PREFIX_DEFAULT: C{str}
    @cvar _PREFIX_DEFAULT: Default prefix.
    @type _DEFAULT_ERRORS: C{dict} {C{str}: C{str}}
    @cvar _DEFAULT_ERRORS: Dictionary mapping default error names to their
        error messages.

    @type prefix: C{str}
    @ivar prefix: Prefix to use for this L{PrefixedIntegerField} instance. 
    """

    _PREFIX_DEFAULT = 'Default value is '

    _DEFAULT_ERRORS = {
        'invalid': 'Enter a whole number.',
        'max_value': 'Ensure this value is less than or equal to %s.',
        'min_value': 'Ensure this value is greater than or equal to %s.',

        # This error message should not ever be displayed; empty fields should
        # be handled in the clean() methods of PreferencesForm and
        # SubscribeForm.
        'empty': 'Please enter a value in this field.',
    }

    def __init__(self, max_value=None, min_value=None, *args, **kwargs):
        """Constructor for L{PrefixedIntegerField}. Passes arguments to 
        C{IntegerField}, and adds validators for min and max values.

        @type max_value: C{int}
        @arg max_value: Maximum allowed value for this L{PrefixedIntegerField}.
        @type min_value: C{int}
        @arg min_value: Minimum allowed value for this L{PrefixedIntegerField}.
        """

        forms.IntegerField.__init__(self, *args, **kwargs)

        self.prefix = PrefixedIntegerField._PREFIX_DEFAULT
        self.error_messages = PrefixedIntegerField._DEFAULT_ERRORS
        self.max_value = max_value
        self.min_value = min_value

    def clean(self, value):
        """Handles the min/max validation provided for fields in Django 1.2
        Throws errors if values are above or below max/min values.
        """

        value = self.to_python(value)
        print 'clean got ' + str(value)

        if self.max_value != None:
            if value > self.max_value:
                raise ValidationError(self.error_messages['max_value' %
                    self.max_value])
        if self.min_value != None:
            if value < self.min_value:
                raise ValidationError(self.error_messages['min_value' %
                    self.max_value])

        return value

    def to_python(self, value):
        """First step in Django's validation process. Ensures that data in
        L{Prefixed IntegerField} is a Python C{int} and returns the data in 
        that form. L{PrefixedIntegerField} is necessary in order to overwrite
        this method; cuts off the prefix and then sends the remaining input to
        the C{IntegerField} C{to_python} method.

        @arg value: The input of the L{PrefixedIntegerField} field.
        @rtype: int
        @return: The data in the input field if it is an integer, with the 
            prefix removed if it is of the form C{PREFIX INTEGER}. 
        @raise ValidationError: If the L{PrefixedIntegerField} is empty. 
            Passes the empty error message so that this error can be caught and
            handled correctly.
        """
        prefix = self.prefix
        # XXX
        print 'Value: ' + str(value)

        if value == '':
            # XXX
            print 'raising empty validation error'
            raise ValidationError(self.error_messages['empty'])

        try:
            if value.startswith(prefix):
                # XXX
                print 'calling superclass clean method with prefix removed'
                value = int(forms.IntegerField.clean(self, 
                    value[len(prefix):]))
            else:
                # XXX
                print 'calling superclass clean method w/o prefix removed'
                value = int(forms.IntegerField.clean(self,
                                                value))
        except (ValueError, TypeError):
            # XXX
            print 'raising invalid validation error'
            raise ValidationError(self.error_messages['invalid'])

        print 'returning value: ' + str(value)
        return value


# FORMS -----------------------------------------------------------------------
# -----------------------------------------------------------------------------

class GenericForm(forms.Form):
    """The basic form class that is inherited by the L{SubscribeForm} class
    and the L{PreferencesForm} class. 
    
    Django uses class variables to specify form fields, but these fields are 
    practically used and thought of as instance variables, so this 
    documentation will refer to them as such. Field types are specified as
    their Django field classes, with parentheses indicating the python type
    they are validated against and treated as practically.
    
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
    @type _NODE_DOWN_GRACE_PD_UNIT_CHOICES: list [tuple (str)]
    @cvar _NODE_DOWN_GRACE_PD_UNIT_CHOICES: List of tuples of backend and 
        frontend names for unit choice for L{node_down_grace_pd_unit}.
    @type _NODE_DOWN_GRACE_PD_UNIT_INIT: tuple (str)
    @cvar _NODE_DOWN_GRACE_PD_UNIT_INIT: Initial tuple for the
        L{node_down_grace_pd_unit} field.
    
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
    @cvar _VERSION_TYPE_INIT: Initial tuple for the L{version_type} field.
    @type _VERSION_SECTION_INFO: str
    @cvar _VERSION_SECTION_INFO: Text explaining the version subscription,
        displayed in the expandable version section of the form, with HTML
        enabled.

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
    @type _T_SHIRT_SECTION_INFO: str
    @cvar _T_SHIRT_SECTION_INFO: Text explaining the t-shirt subscription,
        displayed in the expandable version section of the form, with HTML
        enabled.

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

    @type get_node_down: BooleanField
    @ivar get_node_down: Checkbox letting users choose to subscribe to a
        L{NodeDownSub}.
    @type node_down_grace_pd: L{PrefixedIntegerField}
    @ivar node_down_grace_pd: Integer field (displaying prefix) letting users
        specify their grace period for a L{NodeDownSub}.
    @type node_down_grace_pd_unit: ChoiceField
    @ivar node_down_grace_pd_unit: Unit for L{node_down_grace_pd}. 

    @type get_version: BooleanField
    @ivar get_version: Checkbox letting users choose to subscribe to a 
        L{VersionSub}.
    @type version_type: ChoiceField
    @ivar version_type: Radio button list letting users choose the type of
        L{VersionSub} to subscribe to.
    
    @type get_band_low: BooleanField
    @ivar get_band_low: Checkbox letting users choose to subscribe to a
        L{BandwidthSub}.
    @type band_low_threshold: L{PrefixedIntegerField}
    @ivar band_low_threshold: Integer field (displaying prefix) letting users
        specify their threshold for a L{BandwidthSub}.

    @type get_t_shirt: BooleanField
    @ivar get_t_shirt: Checkbox letting users choose to subscribe to a 
        L{TShirtSub}.
    """
      
    _GET_NODE_DOWN_INIT = True
    _GET_NODE_DOWN_LABEL = 'Email me when the node is down'
    _NODE_DOWN_GRACE_PD_INIT = 1
    _NODE_DOWN_GRACE_PD_MAX = 4500
    _NODE_DOWN_GRACE_PD_MIN = 1
    _NODE_DOWN_GRACE_PD_LABEL = 'How long before we send a notifcation?'
    _NODE_DOWN_GRACE_PD_HELP_TEXT = 'Enter a value between one hour and six \
            months'
    _NODE_DOWN_GRACE_PD_UNIT_CHOICES = [ ('H', 'hours'),
                                         ('D', 'days'),
                                         ('W', 'weeks'),
                                         ('M', 'months') ]
    _NODE_DOWN_GRACE_PD_UNIT_INIT = ('H', 'hours')
    
    _GET_VERSION_INIT = False
    _GET_VERSION_LABEL = 'Email me when the node\'s Tor version is out of date'
    _VERSION_TYPE_CHOICE_1 = 'UNRECOMMENDED'
    _VERSION_TYPE_CHOICE_1_H = 'Recommended Updates'
    _VERSION_TYPE_CHOICE_2 = 'OBSOLETE'
    _VERSION_TYPE_CHOICE_2_H = 'Required Updates'
    _VERSION_TYPE_CHOICES = [ ('UNRECOMMENDED', 'Recommended Updates'),
                              ('OBSOLETE', 'Required Updates') ]
    _VERSION_TYPE_INIT = ('RECOMMENDED', 'Recommended Updates')
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
                     'node_down_grace_pd_unit': _NODE_DOWN_GRACE_PD_UNIT_INIT,
                     'get_version': _GET_VERSION_INIT,
                     'version_type': _VERSION_TYPE_INIT,
                     'get_band_low': _GET_BAND_LOW_INIT,
                     'band_low_threshold': _INIT_PREFIX + \
                             str(_BAND_LOW_THRESHOLD_INIT),
                     'get_t_shirt': _GET_T_SHIRT_INIT}

    get_node_down = forms.BooleanField(required=False,
            label=_GET_NODE_DOWN_LABEL,
            widget=forms.CheckboxInput(attrs={'class':_CLASS_CHECK}))
    node_down_grace_pd = PrefixedIntegerField(required=False,
            min_value=_NODE_DOWN_GRACE_PD_MIN,
            label=_NODE_DOWN_GRACE_PD_LABEL,
            help_text=_NODE_DOWN_GRACE_PD_HELP_TEXT,
            widget=forms.TextInput(attrs={'class':_CLASS_SHORT}))
    node_down_grace_pd_unit = forms.ChoiceField(required=False,
            choices=(_NODE_DOWN_GRACE_PD_UNIT_CHOICES))

    get_version = forms.BooleanField(required=False,
            label=_GET_VERSION_LABEL,
            widget=forms.CheckboxInput(attrs={'class':_CLASS_CHECK}))
    version_type = forms.ChoiceField(required=True,
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
        """Initializes form and creates instance variables for the text
        displayed in the version and t-shirt sections of the form so that the
        template can access them.
        """

        if data == None:
            if initial == None:
                forms.Form.__init__(self, initial=GenericForm._INIT_MAPPING)
            else:
                forms.Form.__init__(self, initial=initial)
        else:
            forms.Form.__init__(self, data)

        self.version_section_text = GenericForm._VERSION_SECTION_INFO
        self.t_shirt_section_text = GenericForm._T_SHIRT_SECTION_INFO

    def check_if_sub_checked(self):
        """Throws a validation error if no subscriptions are checked. 
        Abstracted out of clean() so that there isn't any redundancy in 
        subclass clean() methods.
        """
        
        data = self.cleaned_data

        # Ensures that at least one subscription must be checked.
        if not (data['get_node_down'] or
                data['get_version'] or
                data['get_band_low'] or
                data['get_t_shirt']):
            raise forms.ValidationError('You must choose at least one \
                                         type of subscription!')

    def delete_hidden_errors(self):
        """Deletes errors and supplies default values for fields which are 
        in areas of the form that are collapsed. Returns the manipulated data.
        """

        data = self.cleaned_data
        errors = self._errors

        if 'node_down_grace_pd' in errors and not data['get_node_down']:
            del errors['node_down_grace_pd']
            data['node_down_grace_pd'] = GenericForm._NODE_DOWN_GRACE_PD_INIT
        if 'version_type' in errors and not data['get_version']:
            del errors['version_type']
            data['version_type'] = GenericForm._VERSION_TYPE_INIT
        if 'band_low_threshold' in errors and not data['get_band_low']:
            del errors['band_low_threshold']
            data['band_low_threshold'] = GenericForm._BAND_LOW_THRESHOLD_INIT

    def convert_node_down_grace_pd_unit(self):
        """Converts the L{node_down_grace_pd} to hours, and creates an error
        message if this value in hours is above the maximum allowed value.
        """

        data = self.cleaned_data
        unit = data['node_down_grace_pd_unit']

        if 'node_down_grace_pd' in data:
            grace_pd = data['node_down_grace_pd']

            if unit == 'D':
                grace_pd = grace_pd * 24
            elif unit == 'W':
                grace_pd = grace_pd * 24 * 7
            elif unit == 'M':
                grace_pd = grace_pd * 24 * 30

            if grace_pd > GenericForm._NODE_DOWN_GRACE_PD_MAX:
                del data['node_down_grace_pd']
                del data['node_down_grace_pd_unit']
                self._errors['node_down_grace_pd'] = \
                        self.error_class(['Ensure this time period is \
                        at most six months (4500 hours).'])

            data['node_down_grace_pd'] = grace_pd

    def replace_blank_values(self, replace):
        """Check if C{node_down_grace_pd} and C{band_low_threshold} have errors
        because they are left blank, and then deletes the empty validation 
        error and inserts a value from the C{replace} dictionary.

        @type replace: dict {str: various}
        @arg replace: Dictionary mapping names of fields to their
            values. Meant to either be a dictionary of default values when
            called in SubscribeForm, and the dictionary of the user's previous
            preferences when called in PreferencesForm.
        """

        data = self.cleaned_data

        if 'node_down_grace_pd' in self._errors:
            if PrefixedIntegerField._DEFAULT_ERRORS['empty'] in \
                    str(self._errors['node_down_grace_pd']):
                del self._errors['node_down_grace_pd']
                data['node_down_grace_pd'] = replace['node_down_grace_pd']

        if 'band_low_threshold' in self._errors:
            if PrefixedIntegerField._DEFAULT_ERRORS['empty'] in \
                    str(self._errors['band_low_threshold']):
                del self._errors['band_low_threshold']
                data['band_low_threshold'] = replace['band_low_threshold']

        return data

class SubscribeForm(GenericForm):
    """Form for subscribing to Tor Weather. Inherits from L{GenericForm}.
    The L{SubscribeForm} class contains all the fields in the L{GenericForm}
    class and additional fields for the user's email and the fingerprint of
    the router the user wants to monitor.
    
    @type _EMAIL_1_LABEL: str
    @cvar _EMAIL_1_LABEL: Text displayed above L{email_1} fields.
    @type _EMAIL_MAX_LEN: str
    @cvar _EMAIL_MAX_LEN: Maximum length of L{email_1} fields.
    @type _EMAIL_2_LABEL: str
    @cvar _EMAIL_2_LABEL: Text displayed above L{email_2} fields.
    @type _FINGERPRINT_LABEL: str
    @cvar _FINGERPRINT_LABEL: Text displayed above L{fingerprint} fields.
    @type _FINGERPRINT_MAX_LEN: int
    @cvar _FINGERPRINT_MAX_LEN: Maximum length of L{fingerprint} fields.
    @type _SEARCH_LABEL: str
    @cvar _SEARCH_LABEL: Text displayed above L{router_search} fields.
    @type _SEARCH_MAX_LEN: int
    @cvar _SEARCH_MAX_LEN: Maximum length for L{router_search} fields.
    @type _SEARCH_ID: str
    @cvar _SEARCH_ID: HTML/CSS id for L{router_search} fields.
    @type _CLASS_EMAIL: str
    @cvar _CLASS_EMAIL: HTML/CSS class for L{email_1} and L{email_2} fields.
    @type _CLASS_LONG: str
    @cvar _CLASS_LONG: HTML/CSS class for L{fingerprint} fields.

    @type email_1: EmailField (str)
    @ivar email_1: User's email.
    @type email_2: EmailField (str)
    @ivar email_2: User's email (entered a second time to ensure they entered a
        valid email).
    @type fingerprint: CharField (str)
    @ivar fingerprint: Fingerprint of the router the user wants to monitor.
    @type router_search: CharField (str)
    @ivar router_search: Field to search by router name for a fingerprint.
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

        # XXX
        print '\n\nMaking SubscribeForm:'
        if data != None:
            print '    Initial Data:'
            print '      get_node_down: ' + data['get_node_down']
            print '        node_down_grace_pd: ' + data['node_down_grace_pd']
            print '      get_band_low: ' + data['get_band_low']
            print '        band_low_threshold: ' + data['band_low_threshold']
            print '      full data: ' + str(data)

    def clean(self):
        """Called when the is_valid method is evaluated for a L{SubscribeForm} 
        after a POST request. Calls the same methods that the L{GenericForm}
        L{clean<GenericForm.clean>} method does; also ensures that the two 
        email fields match and fills in default values for 
        L{node_down_grace_pd} and L{band_low_threshold} fields if they are left
        blank.        
        """
        
        data = self.cleaned_data
        
        # Calls the generic clean() helper methods.
        GenericForm.check_if_sub_checked(self)
        GenericForm.convert_node_down_grace_pd_unit(self)
        GenericForm.delete_hidden_errors(self)
        GenericForm.replace_blank_values(self, GenericForm._INIT_MAPPING)

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
        """Called in the validation process before the L{clean} method. Tests
        whether the fingerprint is a valid router in the database, and presents
        an appropriate error message if it isn't. The ValidationError raised
        if the fingerprint isn't in the database is inserted into the form
        through Django's automatic form error handling.
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
        @arg fingerprint: String representation of a router's fingerprint.
        @rtype: bool
        @return: Whether a router with the specified fingerprint exists in
            the database; C{True} if it does, C{False} if it doesn't.
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
        @arg subscriber: The subscriber whose subscriptions are being saved.
        """
        
        # XXX
        print "I'm about to create subscriptions, here's my cleaned_data"
        if 'node_down_grace_pd' in self.cleaned_data:
            print 'node_down_grace_pd: ' + \
                str(self.cleaned_data['node_down_grace_pd'])
        if 'band_low_threshold' in self.cleaned_data:
            print 'band_low_threshold: ' + \
                str(self.cleaned_data['band_low_threshold'])

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

    @type _USER_INFO_STR: str
    @cvar _USER_INFO_STR: Format of user info displayed at the top of the page.

    @type user: L{Subscriber}
    @ivar user: The user/subscriber accessing their preferences.
    @type user_info: str
    @ivar user_info: The email, router name, and router fingerprint of C{user}.
    """
    
    _USER_INFO_STR = '<p><span>Email:</span> %s</p> \
            <p><span>Router Name:</span> %s</p> \
            <p><span>Router Fingerprint:</span> %s</p>'

    def __init__(self, user, data = None):
        """Calls GenericForm __init__ method and saves C{user} and
        C{user_info} instance variables.
        """

        # If no data, is provided, then create using preferences as initial
        # form data. Otherwise, use provided data.
        if data == None:
            GenericForm.__init__(self, initial=user.get_preferences())
        else:
            GenericForm.__init__(self, data)
 
        self.user = user
        self.preferences = self.user.get_preferences()

        self.user_info = PreferencesForm._USER_INFO_STR % (self.user.email, \
                self.user.router.name, user.router.spaced_fingerprint())

    def clean(self):
        """Performs the basic, form-wide cleaning for L{PreferencesForm}. This 
        method is called automatically by Django's form validation. Ensures
        that at least on subscription type is selected, converts the
        L{node_down_grace_pd} to hours and ensures it isn't over the maximum
        allowed value after this conversion, and deletes errors for sections of
        the form corresponding to subscriptions the user isn't subscribing to.
                
        @return: The 'cleaned' data from the POST request.
        """
        
        GenericForm.check_if_sub_checked(self)
        GenericForm.convert_node_down_grace_pd_unit(self)
        GenericForm.delete_hidden_errors(self)
        GenericForm.replace_blank_values(self, self.preferences)

        return self.cleaned_data

    def change_subscriptions(self, new_data):
        """Change the subscriptions and options if they are specified.
       
        @type new_data: dict {str: various}
        @arg new_data: New preferences.
        """

        old_data = self.preferences

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

class DeployedDatetime(models.Model):
    """Stores the date and time when this instance of Tor Weather was first
    deployed. This should only ever have one row, and is used by updaters to 
    populate the router table for 48 hours after deployment without sending
    welcome emails.

    @type deployed: DateTimeField (datetime)
    @ivar deployed: The datetime that this instance of Tor Weather was first
    deployed.
    """

    deployed = models.DateTimeField()

    def __unicode__(self):
        """Returns a unicode representation of C{deployed}

        @rtype: unicode
        @return: A unicode representation of C{deployed}
        """

        return self.deployed

