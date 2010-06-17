import socket
from TorCtl import TorCtl
import ctlutil
import config
from models import ModelAdder

class SubscriptionChecker:
    """A class for checking and updating the various subscription types"""
    
    def __init__(self, ctl_util):
        self.ctl_util = ctl_util
    
    def check_node_down(self):
        """Check if all nodes with node_down subscriptions are up or down, and
        send emails and update subscription data as necessary."""

        #All node down subscriptions
        subscriptions = Subscription.objects.filter(name = "node_down")

        for subscription in subscriptions:
            is_up = subscription.subscriber.router.up 
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

    def check_out_of_date():
        # TO DO ------------------------------------------------- EXTRA FEATURE 
        # IMPLEMENT THIS ------------------------------------------------------
        pass

    def check_below_bandwidth():
        # TO DO ------------------------------------------------- EXTRA FEATURE
        # IMPLEMENT THIS ------------------------------------------------------
        pass

    def check_earn_tshirt():
        # TO DO ------------------------------------------------- EXTRA FEATURE
        # IMPLEMENT THIS ------------------------------------------------------
        pass

    def check_all():
        """Check/update all subscriptions"""
        self.check_node_down()

        #---Add when implemented---
        #self.check_out_of_date()
        #self.check_below_bandwidth()
        #self.check_earn_tshirt()

class RouterUpdater:
    """
    A class for updating the Router table and sending 'welcome' emails
  
    @type ctl_util: CtlUtil
    @ivar ctl_util: A CtlUtil object for handling interactions with
    TorCtl
    """

    def __init__(self, ctl_util = ctlutil.CtlUtil()):
        """
        Default constructor.

        @type ctl_util: CtlUtil
        @param ctl_util: [optional] The CtlUtil object you want to use.
        By default, creates a new CtlUtil instance.
        """

        self.ctl_util = ctl_util

    def update_all(self):
        """Add ORs we haven't seen before to the database and update the
        information of ORs that are already in the database."""

        #set the 'up' flag to False for every router in the DB
        router_set = Router.objects()
        for router in router_set:
            router.up = False

        #Get a list of fingerprint/name tuples in the current descriptor file
        finger_name = ctl_util.get_finger_name_list()

        for router in finger_name:

            finger = router[0]
            name = router[1]
            is_up = ctl_util.is_up(finger)

            if is_up:
                try:
                    router_data = Router.objects.get(fingerprint = finger)
                    router_data.last_seen = datetime.datetime.now()
                    router_data.name = name
                    router_data.up = True
                except DoesNotExist:
                    #let's add it
                    Router.objects.add_default_router(finger, name)

def run_all():
    """Run all updaters/checkers in proper sequence"""
    ctl_util = ctlutil.CtlUtil()
    router_updater = RouterUpdater(ctl_util)
    subscription_checker = SubscriptionChecker(ctl_util)
    router_updater.update_all()
    subscription_checker.check_all()


