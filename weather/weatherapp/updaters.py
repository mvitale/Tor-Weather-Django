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
@var failed: A log file for parsed email addresses that were non-functional. 
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
failed = open('log/failed_emails.txt', 'w')

def check_node_down(email_list):
    """Check if all nodes with L{NodeDownSub} subs are up or down,
    and send emails and update sub data as necessary.
    
    @type email_list: list
    @param email_list: The list of tuples representing emails to send.
    @rtype: list
    @return: The updated list of tuples representing emails to send.
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
                    if sub.emailed == False:
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
    """Checks all L{BandwidthSub} subscriptions, updates the information,
    determines if an email should be sent, and updates email_list.

    @type email_list: list
    @param email_list: The list of tuples representing emails to send.
    @rtype: list
    @return: The updated list of tuples representing emails to send.
    """
    subs = BandwidthSub.objects.all()

    for sub in subs:
        fingerprint = sub.subscriber.router.fingerprint
        if sub.subscriber.confirmed:
            if ctl_util.get_bandwidth(fingerprint) < sub.threshold and\
            sub.emailed == False:
                recipient = sub.subscriber.email
                threshold = sub.threshold
                unsubs_auth = sub.subscriber.unsubs_auth
                pref_auth = sub.subscriber.pref_auth

                email_list.append(emails.bandwidth_tuple(recipient, fingerprint,
                                  threshold, unsubs_auth, pref_auth)) 

                sub.emailed = True

            else:
                sub.emailed = False

            sub.save()
    return email_list

def check_earn_tshirt(email_list):
    """Check all L{TShirtSub} subscriptions and send an email if necessary. 
    If the node is down, the trigger flag set to False. The average 
    bandwidth is calculated if triggered is True. This method uses the 
    should_email method in the TShirtSub class.
    
    @type email_list: list
    @param email_list: The list of tuples representing emails to send.
    @rtype: list
    @return: The updated list of tuples representing emails to send.
    """
   
    subs = TShirtSub.objects.filter(emailed = False)

    for sub in subs:
        if sub.subscriber.confirmed:

            # first, update the database 
            router = sub.subscriber.router
            is_up = router.up
            fingerprint = router.fingerprint
            if not is_up and sub.triggered:
                # reset the data if the node goes down
                sub.triggered = False
                sub.avg_bandwidth = 0
                sub.last_changed = datetime.now()
            elif is_up:
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
    necessary.
    
    @type email_list: list
    @param email_list: The list of tuples representing emails to send.
    @rtype: list
    @return: The updated list of tuples representing emails to send."""

    subs = VersionSub.objects.all()

    for sub in subs:
        if sub.subscriber.confirmed:
            version_type = ctl_util.get_version_type(
                           str(sub.subscriber.router.fingerprint))

            if version_type != 'ERROR':
                if version_type == sub.notify_type and sub.emailed == False:
                
                    fingerprint = sub.subscriber.router.fingerprint
                    recipient = sub.subscriber.email
                    unsubs_auth = sub.subscriber.unsubs_auth
                    pref_auth = sub.subscriber.pref_auth
                    email_list.append(emails.version_tuple(recipient,     
                                                           fingerprint,
                                                           version_type,
                                                           unsubs_auth,
                                                           pref_auth))
                    sub.emailed = True

            #if the user has their desired version type, we need to set emailed
            #to False so that we can email them in the future if we need to
                else:
                    sub.emailed = False
            else:
                logging.INFO("Couldn't parse the version relay %s is running" \
                              % fingerprint)
            sub.save()

    return email_list
        
                
def check_all_subs(email_list):
    """Check/update all subscriptions
    
    @type email_list: list
    @param email_list: The list of tuples representing emails to send.
    @rtype: list
    @return: The updated list of tuples representing emails to send.
    """

    email_list = check_node_down(email_list)
    check_version(email_list)
    check_low_bandwidth(email_list)
    email_list = check_earn_tshirt(email_list)
    return email_list

def update_all_routers(email_list):
    """Add ORs we haven't seen before to the database and update the
    information of ORs that are already in the database. Check if a welcome
    email should be sent and add the email tuples to the list.
    
    @type email_list: list
    @param email_list: The list of tuples representing emails to send.
    @rtype: list
    @return: The updated list of tuples representing emails to send.
    """

    #set the 'up' flag to False for every router in the DB
    router_set = Router.objects.all()
    for router in router_set:
        router.up = False
        router.save()

    #Get a list of fingerprint/name tuples in the current descriptor file
    finger_name = ctl_util.get_finger_name_list()
    print 'fingerprint/name list: %s' % finger_name

    for router in finger_name:
        finger = router[0]
        name = router[1]
        is_up_hiber = ctl_util.is_up_or_hibernating(finger)
        print '%s is up or hibernating: %s' % (name, is_up_hiber)


        if is_up_hiber:
            is_exit = ctl_util.is_exit(finger)

            router_data = None
            try:
                router_data = Router.objects.get(fingerprint = finger)
            except Router.DoesNotExist:
                #let's add it
                Router(fingerprint=finger, name=name, exit = is_exit).save()
                router_data = Router.objects.get(fingerprint = finger)

            router_data.last_seen = datetime.now()
            router_data.name = name
            router_data.up = True
            router_data.exit = is_exit
            #send a welcome email if indicated
            print 'router is welcomed: %s' % router_data.welcomed
            print 'stable: %s' % ctl_util.is_stable(finger)
            if router_data.welcomed == False and ctl_util.is_stable(finger):
                address = ctl_util.get_email(finger)
                print address
                if not address == "":
                    email = emails.welcome_tuple(address, finger, is_exit)
                    email_list.append(email)
                router_data.welcomed = True
            router_data.save()

    return email_list

def run_all():
    """Run all updaters/checkers in proper sequence, send emails."""
    # the list of tuples of email info, gets updated w/ each call
    print 'starting updaters.run_all()'
    email_list = []
    print 'about to update routers'
    email_list = update_all_routers(email_list)
    print 'finished updating routers. email list: %s' % email_list
    print 'about to check all subs'
    email_list = check_all_subs(email_list)
    print 'checked subs. email list: %s' % email_list
    mails = tuple(email_list)

    #-------commented out for safety!---------------
    #try:
    print 'sending emails'
    send_mass_mail(mails, fail_silently=True)
    print 'sent emails'
    #except SMTPException, e:
        #logging.INFO(e)
        #failed.write(e + '\n')
