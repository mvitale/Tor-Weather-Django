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
@var failed_email_file: A log file for parsed email addresses that were non-functional. 
"""
import socket, sys, os
import threading
from datetime import datetime
import time
import logging
from smtplib import SMTPException

from config import config
from weatherapp.ctlutil import CtlUtil
from weatherapp.models import Subscriber, Router, NodeDownSub, BandwidthSub, \
                              TShirtSub, VersionSub, DeployedDatetime
from weatherapp import emails

from django.core.mail import send_mass_mail

failed_email_file = 'log/failed_emails.txt'

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
                if not sub.triggered:
                    sub.triggered = True
                    sub.last_changed = datetime.now()

                if sub.is_grace_passed() and sub.emailed == False:
                    recipient = sub.subscriber.email
                    fingerprint = sub.subscriber.router.fingerprint
                    name = sub.subscriber.router.name
                    grace_pd = sub.grace_pd
                    unsubs_auth = sub.subscriber.unsubs_auth
                    pref_auth = sub.subscriber.pref_auth
                        
                    email = emails.node_down_tuple(recipient, fingerprint, 
                                                   name, grace_pd,          
                                                   unsubs_auth, pref_auth)
                    email_list.append(email)
                    sub.emailed = True 

            sub.save()
    return email_list

def check_low_bandwidth(ctl_util, email_list):
    """Checks all L{BandwidthSub} subscriptions, updates the information,
    determines if an email should be sent, and updates email_list.

    @type ctl_util: CtlUtil
    @param ctl_util: A valid CtlUtil instance.
    @type email_list: list
    @param email_list: The list of tuples representing emails to send.
    @rtype: list
    @return: The updated list of tuples representing emails to send.
    """
    subs = BandwidthSub.objects.all()

    for sub in subs:

        #TorCtl does type checking, so fingerprint needs to be converted from
        #a unicode string to a python str
        fingerprint = str(sub.subscriber.router.fingerprint)

        if sub.subscriber.confirmed:
            bandwidth = ctl_util.get_bandwidth(fingerprint)
            if bandwidth < sub.threshold: 
                if sub.emailed == False:
                    recipient = sub.subscriber.email
                    name = sub.subscriber.router.name
                    threshold = sub.threshold
                    unsubs_auth = sub.subscriber.unsubs_auth
                    pref_auth = sub.subscriber.pref_auth
                    email_list.append(emails.bandwidth_tuple(recipient, 
                    fingerprint, name, bandwidth, threshold, unsubs_auth,
                    pref_auth)) 
                    sub.emailed = True
            else:
                sub.emailed = False
            sub.save()

    return email_list

def check_earn_tshirt(ctl_util, email_list):
    """Check all L{TShirtSub} subscriptions and send an email if necessary. 
    If the node is down, the trigger flag set to False. The average 
    bandwidth is calculated if triggered is True. This method uses the 
    should_email method in the TShirtSub class.

    @type ctl_util: CtlUtil
    @param ctl_util: A valid CtlUtil instance.
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
            fingerprint = str(router.fingerprint)
            if not is_up and sub.triggered:
                # reset the data if the node goes down
                sub.triggered = False
                sub.avg_bandwidth = 0
                sub.last_changed = datetime.now()
            elif is_up:
                descriptor = ctl_util.get_single_descriptor(fingerprint)
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
                    if sub.should_email():
                        recipient = sub.subscriber.email
                        fingerprint = sub.subscriber.router.fingerprint
                        name = sub.subscriber.router.name
                        avg_band = sub.avg_bandwidth
                        time = hours_up
                        exit = sub.subscriber.router.exit
                        unsubs_auth = sub.subscriber.unsubs_auth
                        pref_auth = sub.subscriber.pref_auth
                        
                        email = emails.t_shirt_tuple(recipient, fingerprint,
                                                     name, avg_band, time,
                                                     exit, unsubs_auth, 
                                                     pref_auth)
                        email_list.append(email)
                        sub.emailed = True

            sub.save()
    return email_list

def check_version(ctl_util, email_list):
    """Check/update all C{VersionSub} subscriptions and send emails as
    necessary.

    @type ctl_util: CtlUtil
    @param ctl_util: A valid CtlUtil instance.
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
                if (version_type == 'OBSOLETE' or sub.notify_type == \
                    version_type): 
                    if sub.emailed == False:
                
                        fingerprint = sub.subscriber.router.fingerprint
                        name = sub.subscriber.router.name
                        recipient = sub.subscriber.email
                        unsubs_auth = sub.subscriber.unsubs_auth
                        pref_auth = sub.subscriber.pref_auth
                        email_list.append(emails.version_tuple(recipient,     
                                                               fingerprint,
                                                               name,
                                                               version_type,
                                                               unsubs_auth,
                                                               pref_auth))
                        sub.emailed = True

            #if the user has their desired version type, we need to set emailed
            #to False so that we can email them in the future if we need to
                else:
                    sub.emailed = False
            else:
                logging.info("Couldn't parse the version relay %s is running" \
                              % fingerprint)

            sub.save()

    return email_list
        
                
def check_all_subs(ctl_util, email_list):
    """Check/update all subscriptions
   
    @type ctl_util: CtlUtil
    @param ctl_util: A valid CtlUtil instance.
    @type email_list: list
    @param email_list: The list of tuples representing emails to send.
    @rtype: list
    @return: The updated list of tuples representing emails to send.
    """
    logging.debug('Checking node down subscriptions.')
    email_list = check_node_down(email_list)
    logging.debug('Checking version subscriptions.')
    check_version(email_list)
    logging.debug('Checking bandwidth subscriptions.')
    check_low_bandwidth(email_list)
    logging.debug('Checking shirt subscriptions.')
    email_list = check_earn_tshirt(email_list)
    return email_list

def update_all_routers(ctl_util, email_list):
    """Add ORs we haven't seen before to the database and update the
    information of ORs that are already in the database. Check if a welcome
    email should be sent and add the email tuples to the list.

    @type ctl_util: CtlUtil
    @param ctl_util: A valid CtlUtil instance.
    @type email_list: list
    @param email_list: The list of tuples representing emails to send.
    @rtype: list
    @return: The updated list of tuples representing emails to send.
    """
    
    #determine if two days have passed since deployment and set fully_deployed
    #accordingly
    deployed_query = DeployedDatetime.objects.all()
    if len(deployed_query) == 0:
        #then this is the first time that update_all_routers has run,
        #so create a DeployedDatetime with deployed set to now.
        deployed = datetime.now()
        DeployedDatetime(deployed = deployed).save()
    else:
        deployed = deployed_query[0].deployed
    if (datetime.now() - deployed).days < 2:
        fully_deployed = False
    else:
        fully_deployed = True
    
    router_set = Router.objects.all()
    for router in router_set:
        #remove routers from the db that we haven't seen for more than a year 
        if (datetime.now() - router.last_seen).days > 365:
            router.delete()
        #Set the 'up' flag to False for every router
        else:
            router.up = False
            router.save()
    
    #Get a list of fingerprint/name tuples in the current descriptor file
    finger_name = ctl_util.get_finger_name_list()

    for router in finger_name:
        finger = router[0]
        name = router[1]

        if ctl_util.is_up_or_hibernating(finger):

            router_data = None
            try:
                router_data = Router.objects.get(fingerprint = finger)
            except:
                if fully_deployed:
                    router_data = Router(name = name, fingerprint = finger,
                                         welcomed = False)
                else:
                    #We don't ever want to welcome relays that were running 
                    #when  Weather was deployed, so set welcomed to True
                    router_data = Router(name = name, fingerprint = finger,
                                         welcomed = True)           
            
            router_data.last_seen = datetime.now()
            router_data.name = name
            router_data.up = True
            router_data.exit = ctl_util.is_exit(finger)

            #send a welcome email if indicated
            if router_data.welcomed == False and ctl_util.is_stable(finger):
                address = ctl_util.get_email(finger)
                if not address == "":
                    email = emails.welcome_tuple(address, finger, name, is_exit)
                    email_list.append(email)
                router_data.welcomed = True

            router_data.save()

    return email_list

def run_all():
    """Run all updaters/checkers in proper sequence, then send emails."""

    #The CtlUtil for all methods to use
    ctl_util = CtlUtil()

    # the list of tuples of email info, gets updated w/ each call
    email_list = []
    email_list = update_all_routers(ctl_util, email_list)
    logging.info('Finished updating routers. About to check all subscriptions.')
    email_list = check_all_subs(ctl_util, email_list)
    logging.info('Finished checking subscriptions. About to send emails.')
    mails = tuple(email_list)

    try:
        send_mass_mail(mails, fail_silently = False)
    except SMTPException, e:
        logging.info(e)
        failed = open(failed_email_file, 'w')
        failed.write(e + '\n')
        failed.close()
    logging.info('Finished sending emails.')
