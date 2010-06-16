import socket
from TorCtl import TorCtl
import ctlutil
import config

class SubscriptionChecker:
    """A class for checking and updating the various subscription types"""
    
    # TO DO ------------------------------------------------------ BASE FEATURE
    # UPDATE CLASS TO WORK WITH CTLUTIL ---------------------------------------

    def __init__(self):
        self.pinger = TorPing()

    def check_all_down(self):
        """Check if all nodes with node_down subscriptions are up or down, and
        send emails and update subscription data as necessary."""

        #All node down subscriptions
        subscriptions = Subscription.objects.filter(name = "node_down")

        for subscription in subscriptions:
            is_up = self.pinger.ping( 
                    subscription.subscriber.router.fingerprint) 
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
        return

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

class RouterUpdater:
    """A class for updating the Router table and sending 'welcome' emails"""

    # TO DO ------------------------------------------------------ BASE FEATURE
    # UPDATE CLASS TO WORK WITH CTLUTIL ---------------------------------------

    def __init__(self):
        self.ctl_util = ctlutil.CtlUtil()

    def update_all(self):
        """Add ORs we haven't seen before to the database and update the
        information of ORs that are already in the database."""

        finger_name = ctl_util.get_finger_name_list()

        for router in finger_name:

            finger = router[0]
            name = router[1]
            is_up = ctl_util.ping(finger)

            if is_up:
                try:
                    router_data = Router.objects.get(fingerprint = finger)
                    router_data.last_seen = datetime.datetime.now()
                    router_data.name = name
                except DoesNotExist:
                    #let's add it
                    new_router = Router(finger, name, False,
                                        datetime.datetime.now())
        return
