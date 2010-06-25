import socket, sys, os
import ctlutil
import config
from emails import Emailer
import datetime 
from models import *

class SubscriptionChecker:
    """A class for checking and updating the various subscription types"""
    
    def __init__(self, ctl_util):
        self.ctl_util = ctl_util
    
    def check_node_down(self):
        """Check if all nodes with node_down subscriptions are up or down, and
        send emails and update subscription data as necessary."""

        #All node down subscriptions
        subscriptions = NodeDownSub.objects.all()

        for subscription in subscriptions:
            #only check subscriptions of confirmed subscribers
            if subscription.subscriber.confirmed:

                is_up = subscription.subscriber.router.up 
                if is_up:
                    if subscription.triggered:
                       subscription.triggered = False
                       subscription.last_changed = datetime.now()
                else:
                    if subscription.triggered:
                        #if subscription.should_email():------enable after debugging---
                        recipient = subscription.subscriber.email
                        fingerprint = subscription.subscriber.router.fingerprint
                        grace_pd = subscription.grace_pd
                        unsubs_auth = subscription.subscriber.unsubs_auth
                        pref_auth = subscription.subscriber.pref_auth
                        
                        Emailer.send_node_down(recipient, fingerprint, grace_pd,
                                                unsubs_auth, pref_auth)
                        subscription.emailed = True 
                    else:
                        subscription.triggered = True
                        subscription.last_changed = datetime.now()
                subscription.save()

    def check_out_of_date(self):
        # TO DO ------------------------------------------------- EXTRA FEATURE 
        # IMPLEMENT THIS ------------------------------------------------------
        pass

    def check_below_bandwidth(self):
        # TO DO ------------------------------------------------- EXTRA FEATURE
        # IMPLEMENT THIS ------------------------------------------------------
        pass

    def check_earn_tshirt(self):
        # TO DO ------------------------------------------------- EXTRA FEATURE
       # IMPLEMENT THIS ------------------------------------------------------
        pass

    def check_all(self):
        """Check/update all subscriptions"""
        self.check_node_down()

        #---Add when implemented---
        #self.check_out_of_date()
        #self.check_below_bandwidth()
        #self.check_earn_tshirt()

class RouterUpdater:
    """
    A class for updating the Router table and sending 'welcome' emails
    (welcome email feature not yet implemented)
  
    @type ctl_util: CtlUtil
    @ivar ctl_util: A CtlUtil object for handling interactions with
    TorCtl
    """

    def __init__(self, ctl_util = None):
        """
        Default constructor.

        @type ctl_util: CtlUtil
        @param ctl_util: [optional] The CtlUtil object you want to use.
        By default, creates a new CtlUtil instance.
        """
        self.ctl_util = ctl_util

        if not ctl_util:
            self.ctl_util = ctlutil.CtlUtil()

    def update_all(self):
        """Add ORs we haven't seen before to the database and update the
        information of ORs that are already in the database."""

        #set the 'up' flag to False for every router in the DB
        router_set = Router.objects.all()
        for router in router_set:
            router.up = False
            router.save()

        #Get a list of fingerprint/name tuples in the current descriptor file
        finger_name = self.ctl_util.get_finger_name_list()

        for router in finger_name:

            finger = router[0]
            name = router[1]
            is_up = self.ctl_util.is_up(finger)

            if is_up:
                try:
                    router_data = Router.objects.get(fingerprint = finger)
                    router_data.last_seen = datetime.now()
                    router_data.name = name
                    router_data.up = True
                    router_data.save()
                except Router.DoesNotExist:
                    #let's add it
                    Router(fingerprint=finger, name=name).save()

class Welcomer:
    """A class for informing new relay operators about Weather"""
    def __init__(self, ctl_util = None):
        self.ctl_util = ctl_util
        if ctl_util == None:
            ctl_util = ctlutil.CtlUtil()

    def welcome(self):
        """Send welcome emails to new, stable relay operators"""
        uninformed = Router.objects.filter(welcomed = False)
        for router in uninformed:
            if self.ctl_util.is_stable(router.fingerprint):
                email = self.ctl_util.get_email(router.fingerprint)
                if not email == "":
                   Emailer.send_welcome(email)
                
                #Even if we can't get a router's email, we set welcomed to true
                #so that we don't keep trying to parse their email
                router.welcomed = True
                router.save()
def main():
    """Run all updaters/checkers in proper sequence"""
    ctl_util = ctlutil.CtlUtil()
    router_updater = RouterUpdater(ctl_util)
    welcome = Welcomer(ctl_util)
    subscription_checker = SubscriptionChecker(ctl_util)
    router_updater.update_all()
    welcome.welcome()
    subscription_checker.check_all()

if __name__ == "__main__":
    main()


