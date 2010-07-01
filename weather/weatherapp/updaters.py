"""This module's run_all() method is called when a new consensus event is 
triggered in listener.py. It first populates and updates
the Router table by storing new routers seen in the consensus document and 
updating info relating to routers already stored. Next, each subscription is 
checked to determine if the Subscriber should be emailed. When an email 
notification is indicated, a tuple with the email subject, message, sender, and 
recipient is added to the list of email tuples. Once all updates are complete, 
Django's send_mass_mail method is called, passing in the emails tuple as a 
parameter.

@type ctl_util: CtlUtil
@var ctl_util: A CtlUtil object for the module to handle the connection to and
    communication with TorCtl.
"""
import socket, sys, os
import threading
import datetime
import time
import logging
from smtplib import SMTPException

from weatherapp.ctlutil import CtlUtil
from weatherapp.models import *
import weatherapp.emails
from config import config 

from django.core.mail import send_mass_mail

#a CtlUtil instance module attribute
ctl_util = CtlUtil()
failed = open('failed_emails.txt', 'w')

def check_node_down(email_list):
    """Check if all nodes with L{NodeDownSub} subs are up or down,
    and send emails and update sub data as necessary.
    
    @type email_list: list
    @param email_list: The list of tuples containing email info.
    @rtype: list
    @return: The updated list of tuples containing email info.
    """
    #All node down subs
    subs = NodeDownSub.objects.all()

    for sub in subs:
        #only check subscriptions of confirmed subscribers
        if sub.subscriber.confirmed:

            if sub.subscriber.router.up:
                if sub.triggered:
                   sub.triggered = False
                   sub.emailed = False
                   sub.last_changed = datetime.now()
            else:
                if sub.triggered:
                    #if sub.is_grace_passed() and sub.emailed == False:------enable after debugging---
                    recipient = sub.subscriber.email
                    fingerprint = sub.subscriber.router.fingerprint
                    grace_pd = sub.grace_pd
                    unsubs_auth = sub.subscriber.unsubs_auth
                    pref_auth = sub.subscriber.pref_auth
                    
                    email = emails.node_down_tuple(recipient, fingerprint, 
                                                   grace_pd, unsubs_auth,
                                                   pref_auth)
                    email_list.append(email)
                    sub.emailed = True 
                else:
                    sub.triggered = True
                    sub.last_changed = datetime.now()

            sub.save()
    return email_list

def check_low_bandwidth(email_list):
    """Checks all L{LowBandwidthSub} subscriptions, updates the information,
    determines if an email should be sent, and updates email_list.

    @type email_list: list
    @param email_list: The list of tuples containing email info.
    @rtype: list
    @return: The updated list of tuples containing email info.
    """
    subs = BandwidthSub.objects.all()

    for sub in subs:
        fingerprint = sub.subscriber.fingerprint
        if sub.subscriber.confirmed:
            if self.ctlutil.get_bandwidth(fingerprint) < sub.threshold and\
            sub.emailed == False:
                if sub.triggered and sub.is_grace_passed():
                    recipient = sub.subscriber.email
                    grace_pd = sub.grace_pd
                    unsubs_auth = sub.subscriber.unsubs_auth
                    pref_auth = sub.subscriber.pref_auth

                    email_list.append(emails.bandwidth_tuple(recipient,         
                    grace_pd, unsubs_auth, pref_auth)) 

                    sub.emailed = True

                elif not sub.triggered:
                    sub.triggered = True
                    sub.last_changed = datetime.now()
            else:
                if sub.triggered:
                    sub.triggered = False
                    sub.emailed = False
                    sub.last_changed = datetime.now()

            sub.save()
    return email_list

def check_earn_tshirt(email_list):
    """Check all L{TShirtSub} subscriptions and send an email if necessary. 
    If the node is down, the trigger flag set to False. The average 
    bandwidth is calculated if triggered is True. This method uses the 
    should_email method in the TShirtSub class.
    
    @type email_list: list
    @param email_list: The list of tuples containing email info.
    @rtype: list
    @return: The updated list of tuples containing email info.
    """
   
    subs = TShirtSub.objects.filter(emailed = False)

    for sub in subs:
        if sub.subscriber.confirmed:

            # first, update the database 
            router = sub.subscriber.router
            is_up = router.up
            fingerprint = router.fingerprint
            if not is_up:
                # reset the data if the node goes down
                sub.triggered = False
                sub.avg_bandwidth = 0
                sub.last_changed = datetime.now()
            else:
                descriptor = ctl_ultil.get_single_descriptor(fingerprint)
                current_bandwidth = ctl_util.get_bandwidth(fingerprint)
                if sub.triggered == False:
                # router just came back, reset values
                    sub.triggered = True
                    sub.avg_bandwidth = current_bandwidth
                    sub.last_changed = datetime.now()
                else:
                # update the avg bandwidth (arithmetic)
                    hours_up = sub.get_hours_since_triggered()
                    sub.avg_bandwidth = ctl_util.get_new_avg_bandwidth(
                                                sub.avg_bandwidth,
                                                hours_up,
                                                current_bandwidth)

                    #send email if needed
                    if sub.should_email(hours_up):
                        recipient = sub.subscriber.email
                        avg_band = sub.avg_bandwidth
                        time = sub.hours_since_triggered
                        exit = sub.subscriber.router.exit
                        unsubs_auth = sub.subscriber.unsubs_auth
                        pref_auth = sub.subscriber.pref_auth
                        
                        email = emails.t_shirt_tuple(recipient, avg_band, time,
                                        exit, unsubs_auth, pref_auth)
                        email_list.append(email)
                        sub.emailed = True

            sub.save()
    return email_list

def check_version(email_list):
    """Check/update all C{VersionSub} subscriptions and send emails as
    necessary."""

    subs = VersionSub.objects.all()

    for sub in subs:
        version_type = ctlutil.get_version_type(sub.subscriber.fingerprint)
        if sub.subscriber.confirmed:
            if version_type == sub.notify_type and sub.emailed == False:
            
                fingerprint = sub.subscriber.fingerprint
                recipient = sub.subscriber.email
                unsubs_auth = sub.subscriber.unsubs_auth
                pref_auth = sub.subscriber.pref_auth
                email_list.append(emails.version_tuple(recipient, fingerprint,
                                                       unsubs_auth, pref_auth))
                sub.emailed = True

        #if the user has their desired version type, we need to set emailed
        #to False so that we can email them in the future if we need to
            else:
                sub.emailed = False

        
                
def check_all_subs(email_list):
    """Check/update all subscriptions
    
    @type email_list: list
    @param email_list: The list of tuples containing email info.
    @rtype: list
    @return: The updated list of tuples containing email info.
    """

    email_list = check_node_down(email_list)
    #---Add when implemented---
    #check_version(email_list)
    check_low_bandwidth(email_list)
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
                if router_data.welcomed == False and ctl_util.is_stable(finger):
                    email = ctl_util.get_email(finger)
                    if not email == "":
                        email = emails.welcome_tuple(email, finger, is_exit)
                        email_list.append(email)
                    router_data.welcomed = True
                router_data.save()
            except Router.DoesNotExist:
                #let's add it
                Router(fingerprint=finger, name=name, exit = is_exit).save()
    return email_list

def run_all():
    """Run all updaters/checkers in proper sequence, send emails."""
    # the list of tuples of email info, gets updated w/ each call
    email_list = []
    email_list = update_all_routers(email_list)
    email_list = check_all_subs(email_list)
    mails = tuple(email_list)

    #-------commented out for safety!---------------
    #try:
        #send_mass_mail(mails)
    #except SMTPException, e:
        #logging.INFO(e)
        #failed.write(e + '\n')


if __name__ == "__main__":
    run_all()
