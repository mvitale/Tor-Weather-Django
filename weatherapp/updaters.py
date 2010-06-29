"""This module's run_all() method is called when a new consensus event is 
triggered in listener.py. The cascade of events first populates and updates
the Router table by storing new routers seen in the consensus document and 
updating info relating to routers already stored. Next, each Subscription is 
checked to determine if the Subscriber should be emailed. When an email 
notification is indicated, a tuple with the email subject, message, sender, and 
recipient is added to the list of email tuples. Once all updates are complete, 
Django's send_mass_mail method is called, passing in the emails tuple as a 
parameter.
"""
import socket, sys, os
import threading
import datetime 
import time
import logging

import ctlutil
import config
from models import *

import emails

from django.core.mail import send_mass_mail

ctl_util = ctlutil.CtlUtil()

def check_node_down(email_list):
    """Check if all nodes with L{NodeDownSub} subscriptions are up or down,
    and send emails and update subscription data as necessary.
    
    @type email_list: list
    @param email_list: The list of tuples containing email info.
    @rtype: list
    @return: The updated list of tuples containing email info.
    """
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
                    
                    email = emails.node_down_tuple(recipient, fingerprint, 
                                                   grace_pd, unsubs_auth,
                                                   pref_auth)
                    email_list.append(email)
                    subscription.emailed = True 
                    #else:
                        #subscription.triggered = True
                        #subscription.last_changed = datetime.now()
                subscription.save()
    return email_list

def check_out_of_date(email_list):
    """
    
    @type email_list: list
    @param email_list: The list of tuples containing email info.
    @rtype: list
    @return: The updated list of tuples containing email info.
    """
    # TO DO ------------------------------------------------- EXTRA FEATURE 
    # IMPLEMENT THIS ------------------------------------------------------
    return email_list

def check_below_bandwidth(email_list):
    """
    
    @type email_list: list
    @param email_list: The list of tuples containing email info.
    @rtype: list
    @return: The updated list of tuples containing email info.
    """
    # TO DO ------------------------------------------------- EXTRA FEATURE
    # IMPLEMENT THIS ------------------------------------------------------
    return email_list

def check_earn_tshirt(email_list):
    """Check all L{TShirtSub} subscriptions and send an email if necessary. 
    If the node is down, the trigger flag set to False. The average 
    bandwidth is calculated if triggered is True. This method uses the 
    should_email method in the TShirtSub class."""

    subscriptions = TShirtSub.objects.all()

    for subscription in subscriptions:
        # first, update the database 
        router = subscription.subscriber.router
        is_up = router.up
        fingerprint = router.fingerprint
        if not is_up:
            # reset the data if the node goes down
            subscription.triggered = False
            subscription.avg_bandwidth = 0
            subscription.hours_since_triggered = 0
        else:
            descriptor = ctl_ultil.get_single_descriptor(fingerprint)
            current_bandwidth = ctl_util.get_bandwidth(descriptor)
            if subscription.triggered == False:
            # router just came back, reset values
                subscription.triggered = True
                subscription.avg_bandwidth = current_bandwidth
                subscription.hours_since_triggered = 1
            else:
            # update the avg bandwidth (arithmetic)
                subscription.avg_bandwidth = ctl_util.get_new_avg_bandwidth(
                                            subscription.avg_bandwidth,
                                            subscription.hours_since_triggered,
                                            current_bandwidth)
                subscription.hours_since_triggered+=1
        subscription.save()

        # now send the email if it's needed
        if subscription.should_email():
            recipient = subscription.subscriber.email
            avg_band = subscription.avg_bandwidth
            time = subscription.hours_since_triggered
            exit = subscription.subscriber.router.exit
            unsubs_auth = subscription.subscriber.unsubs_auth
            pref_auth = subscription.subscriber.pref_auth
            
            email = emails.t_shirt_tuple(recipient, avg_band, time, exit, 
                                         unsubs_auth, pref_auth])
            email_list.append(email)
            subscription.emailed = True

    return email_list

def check_version():
    """Check/update all C{VersionSub} subscriptions and send emails as
    necessary."""

    subs = VersionSub.objects.all()

    for sub in subs:
        
                
def check_all_subs(email_list):
    """Check/update all subscriptions
    
    @type email_list: list
    @param email_list: The list of tuples containing email info.
    @rtype: list
    @return: The updated list of tuples containing email info.
    """

    email_list = check_node_down(email_list)
    #---Add when implemented---
    #check_out_of_date(email_list)
    #check_below_bandwidth(email_list)
    email_list = check_earn_tshirt(email_list)
    return email_list

def update_all_routers(email_list):
    """Add ORs we haven't seen before to the database and update the
    information of ORs that are already in the database. Check if a welcome
    email should be sent and add the email tuples to the list.
    
    @type email_list: list
    @param email_list: The list of tuples containing email info.
    @rtype: list
    @return: The updated list of tuples containing email info.
    """

    #set the 'up' flag to False for every router in the DB
    router_set = Router.objects.all()
    for router in router_set:
        router.up = False
        router.save()

    #Get a list of fingerprint/name tuples in the current descriptor file
    finger_name = ctl_util.get_finger_name_list()

    for router in finger_name:

        finger = router[0]
        name = router[1]
        is_up_hiber = ctl_util.is_up_or_hibernating(finger)

        if is_up_hiber:
            is_exit = ctl_util.is_exit(finger)
            try:
                router_data = Router.objects.get(fingerprint = finger)
                router_data.last_seen = datetime.now()
                router_data.name = name
                router_data.up = True
                router_data.exit = is_exit
                #send a welcome email if indicated
                if (router_data.welcomed == False and 
                    ctl_util.is_stable(finger)):
                    email = ctl_util.get_email(finger)
                    if not email == "":
                        email = emails.welcome_tuple(email, finger, is_exit)
                        email_list.append(email)
# ---------------------------- ADD THIS TO THE EMAIL LIST! ------------------
                    router_data.welcomed = True
                router_data.save()
            except Router.DoesNotExist:
                #let's add it
                Router(fingerprint=finger, name=name, exit = is_exit).save()
    return email_list

def run_all():
    """Run all updaters/checkers in proper sequence, send emails"""
    # the list of tuples of email info, gets updated w/ each call
    email_list = []
    email_list = update_all_routers(email_list)
    email_list = check_all_subs(email_list)
    tupl = tuple(email_list)
    send_mass_mail(tupl, fail_silently=True)

if __name__ == "__main__":
    run_all()


