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

def check_all_subs(email_list):
    """Check/update all subscriptions
   
    @type email_list: list
    @param email_list: The list of tuples representing emails to send.
    @rtype: list
    @return: The updated list of tuples representing emails to send.
    """
    for sub_type in models.subscription_types:
        all_subs = sub_type.objects.all()
        for sub in all_subs:
            if sub.subscriber.confirmed:
                sub.update()
                if sub.shoud_email():
                    email_list = email_list + sub.get_email()
                    sub.emailed = True
                    sub.save()
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
