"""
The test module. To run tests, cd to weather and run 'python manage.py
test weatherapp'.
"""
import time
from datetime import datetime, timedelta

from weather.weatherapp.models import Subscriber, Subscription, Router,\
                                      NodeDownSub, TShirtSub, VersionSub,\
                                      BandwidthSub
import emails
from ctlutil import CtlUtil

from django.test import TestCase
from django.test.client import Client
from django.core import mail

class TestWeb(TestCase):
    """Tests the Tor Weather application via post requests"""

    def setUp(self):
        """Set up the test database with a dummy router"""
        self.client = Client()
        r = Router(fingerprint = '1234', name = 'abc', exit=True)
        r.save()

    def test_subscribe_node_down(self):
        """Test a node down subscription (all other subscriptions off)"""
        response = self.client.post('/subscribe/', {'email_1':'name@place.com',
                                          'email_2' : 'name@place.com',
                                          'fingerprint' : '1234',
                                          'get_node_down' : True,
                                          'node_down_grace_pd' : '',
                                          'get_version' : False,
                                          'version_type' : 'OBSOLETE',
                                          'get_band_low': False,
                                          'band_low_threshold' : '',
                                          'get_t_shirt' : False},
                                          follow = True)

        #we want to be redirected to the pending page
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template[0].name, 'pending.html')

        #Check that the correct information was stored
        subscriber = Subscriber.objects.get(email = 'name@place.com')
        self.assertEqual(subscriber.email, 'name@place.com')
        self.assertEqual(subscriber.router.fingerprint, '1234')
        self.assertEqual(subscriber.confirmed, False)
        
        #Test that one message has been sent
        for i in range(0, 100, 1):
            if len(mail.outbox) == 1:
                break
            time.sleep(0.1)

        self.assertEqual(len(mail.outbox), 1)

        #get the email message, make sure the confirm link works
        body = mail.outbox[0].body
        lines = body.split('\n')
        for line in lines:
            if '/confirm' in line:
                link = line.strip()
                self.client.get(link)

                #reload subscriber
                subscriber = Subscriber.objects.get(email = 'name@place.com')
                self.assertEqual(subscriber.confirmed, True)

        #Verify that the subject of the message is correct.
        self.assertEqual(mail.outbox[0].subject, 
                          '[Tor Weather] Confirmation Needed')

        # there should only be one subscription for this subscriber
        subscription_list = Subscription.objects.filter(subscriber = subscriber)
        self.assertEqual(len(subscription_list), 1)
        node_down_sub = NodeDownSub.objects.get(subscriber = subscriber)
        self.assertEqual(node_down_sub.emailed, False)
        self.assertEqual(node_down_sub.triggered, False)
        self.assertEqual(node_down_sub.grace_pd, 1)
    
    def test_subscribe_version(self):
        """Test a version subscription (all other subscriptions off)"""
        response = self.client.post('/subscribe/', {'email_1':'name@place.com',
                                          'email_2' : 'name@place.com',
                                          'fingerprint' : '1234',
                                          'get_node_down' : False,
                                          'node_down_grace_pd' : '',
                                          'get_version' : True,
                                          'version_type' : 'UNRECOMMENDED',
                                          'get_band_low': False,
                                          'band_low_threshold' : '',
                                          'get_t_shirt' : False},
                                          follow = True)
        #we want to be redirected to the pending page
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template[0].name, 'pending.html')
        
        #test that the subscriber was stored correctly
        subscriber = Subscriber.objects.get(email = 'name@place.com')
        self.assertEqual(subscriber.email, 'name@place.com')
        self.assertEqual(subscriber.router.fingerprint, '1234')
        self.assertEqual(subscriber.confirmed, False)
        
        # there should only be one subscription for this subscriber
        subscription_list = Subscription.objects.filter(subscriber = subscriber)
        self.assertEqual(len(subscription_list), 1)

        #Verify that the subscription info was stored correctly
        version_sub = VersionSub.objects.get(subscriber = subscriber)
        self.assertEqual(version_sub.emailed, False)
        self.assertEqual(version_sub.notify_type, 'UNRECOMMENDED')

        #Test that one message has been sent
        for i in range(0, 100, 1):
            if len(mail.outbox) == 1:
                break
            time.sleep(0.1)
        self.assertEqual(len(mail.outbox), 1)

        #get the email message, make sure the confirm link works
        body = mail.outbox[0].body
        lines = body.split('\n')
        for line in lines:
            if '/confirm' in line:
                link = line.strip()
                self.client.get(link)

                #reload subscriber
                subscriber = Subscriber.objects.get(email = 'name@place.com')

                self.assertEqual(subscriber.confirmed, True)

        #Verify that the subject of the message is correct.
        self.assertEquals(mail.outbox[0].subject, 
                          '[Tor Weather] Confirmation Needed')

            
    def test_subscribe_bandwidth(self):
        """Test a bandwidth only subscription attempt"""
        response = self.client.post('/subscribe/', {'email_1':'name@place.com',
                                          'email_2': 'name@place.com',
                                          'fingerprint' : '1234', 
                                          'get_node_down': False,
                                          'node_down_grace_pd' : '',
                                          'get_version' : False,
                                          'version_type' : 'OBSOLETE',
                                          'get_band_low' : True,
                                          'band_low_threshold' : 40,
                                          'get_t_shirt' : False},
                                          follow = True)
        #We want to be redirected to the pending page
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template[0].name, 'pending.html')

        #Check if the correct subscriber info was stored
        subscriber = Subscriber.objects.get(email = 'name@place.com')
        self.assertEqual(subscriber.email, 'name@place.com')
        self.assertEqual(subscriber.router.fingerprint, '1234')
        self.assertEqual(subscriber.confirmed, False)

        #Verify that the subscription was stored correctly 
        bandwidth_sub = BandwidthSub.objects.get(subscriber = subscriber)
        self.assertEqual(bandwidth_sub.emailed, False)
        self.assertEqual(bandwidth_sub.threshold, 40)

        #Test that one message has been sent
        for i in range(0, 100, 1):
            if len(mail.outbox) == 1:
                break
            time.sleep(0.1)
        self.assertEqual(len(mail.outbox), 1)

        #Check if the correct subscriber info was stored
        subscriber = Subscriber.objects.get(email = 'name@place.com')
        self.assertEqual(subscriber.email, 'name@place.com')
        self.assertEqual(subscriber.router.fingerprint, '1234')
        self.assertEqual(subscriber.confirmed, False)

        #Verify that the subscription was stored correctly 
        bandwidth_sub = BandwidthSub.objects.get(subscriber = subscriber)
        self.assertEqual(bandwidth_sub.emailed, False)
        
        #get the email message, make sure the confirm link works
        body = mail.outbox[0].body
        lines = body.split('\n')
        for line in lines:
            if '/confirm' in line:
                link = line.strip()
                self.client.get(link)

                #reload subscriber
                subscriber = Subscriber.objects.get(email = 'name@place.com')

                self.assertEqual(subscriber.confirmed, True)

        #Verify that the subject of the message is correct.
        self.assertEqual(mail.outbox[0].subject, 
                          '[Tor Weather] Confirmation Needed')



    def test_subscribe_shirt(self):
        """Test a t-shirt only subscription attempt"""
        response = self.client.post('/subscribe/', {'email_1':'name@place.com',
                                          'email_2' : 'name@place.com',
                                          'fingerprint' : '1234',
                                          'get_node_down' : False,
                                          'node_down_grace_pd' : 1,
                                          'get_version' : False,
                                          'version_type' : 'UNRECOMMENDED',
                                          'get_band_low' : False,
                                          'band_low_threshold' : '',
                                          'get_t_shirt' : True},
                                          follow = True)

         #We want to be redirected to the pending page
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template[0].name, 'pending.html')

        #Check if the correct subscriber info was stored
        subscriber = Subscriber.objects.get(email = 'name@place.com')
        self.assertEqual(subscriber.email, 'name@place.com')
        self.assertEqual(subscriber.router.fingerprint, '1234')
        self.assertEqual(subscriber.confirmed, False)

        # there should only be one subscription for this subscriber
        subscription_list = Subscription.objects.filter(subscriber = subscriber)
        self.assertEqual(len(subscription_list), 1)

        #Verify that the subscription was stored correctly
        shirt_sub = TShirtSub.objects.get(subscriber = subscriber)
        self.assertEqual(shirt_sub.emailed, False)
        self.assertEqual(shirt_sub.avg_bandwidth, 0)       

        #Test that one message has been sent
        for i in range(0, 100, 1):
            if len(mail.outbox) == 1:
                break
            time.sleep(0.1)
        self.assertEqual(len(mail.outbox), 1)
    
        #get the email message, make sure the confirm link works
        body = mail.outbox[0].body
        lines = body.split('\n')
        for line in lines:
            if '/confirm' in line:
                link = line.strip()
                self.client.get(link)

                #reload subscriber
                subscriber = Subscriber.objects.get(email = 'name@place.com')

                self.assertEqual(subscriber.confirmed, True)

        #Verify that the subject of the message is correct.
        self.assertEqual(mail.outbox[0].subject, 
                          '[Tor Weather] Confirmation Needed')



    def test_subscribe_all(self):
        """Test a subscribe attempt to all subscription types, relying
        on default values."""
        response = self.client.post('/subscribe/', {'email_1':'name@place.com',
                                          'email_2' : 'name@place.com',
                                          'fingerprint' : '1234',
                                          'get_node_down' : True,
                                          'node_down_grace_pd' : '',
                                          'get_version' : True,
                                          'version_type' : 'UNRECOMMENDED',
                                          'get_band_low': True,
                                          'band_low_threshold' : '',
                                          'get_t_shirt' : True},
                                          follow = True)

        # we want to be redirected to the pending page
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template[0].name, 'pending.html')

        # check that the subscriber was added correctly
        subscriber = Subscriber.objects.get(email = 'name@place.com')
        self.assertEqual(subscriber.email, 'name@place.com')
        self.assertEqual(subscriber.router.fingerprint, '1234')
        self.assertEqual(subscriber.confirmed, False)

        # there should be four subscriptions for this subscriber
        subscription_list = Subscription.objects.filter(subscriber = subscriber)
        self.assertEqual(len(subscription_list), 4)
        
        node_down_sub = NodeDownSub.objects.get(subscriber = subscriber)
        self.assertEqual(node_down_sub.emailed, False)
        self.assertEqual(node_down_sub.triggered, False)
        self.assertEqual(node_down_sub.grace_pd, 1)
        
        version = VersionSub.objects.get(subscriber = subscriber)
        self.assertEqual(version.emailed, False)
        self.assertEqual(version.notify_type, 'UNRECOMMENDED')

        bandwidth = BandwidthSub.objects.get(subscriber = subscriber)
        self.assertEqual(bandwidth.emailed, False)
        self.assertEqual(bandwidth.threshold, 20)
        
        tshirt = TShirtSub.objects.get(subscriber = subscriber)
        self.assertEqual(tshirt.avg_bandwidth, 0)
        self.assertEqual(tshirt.emailed, False)

        #Test that one message has been sent
        for i in range(0, 100, 1):
            if len(mail.outbox) == 1:
                break
            time.sleep(0.1)
        self.assertEqual(len(mail.outbox), 1)
    
        #get the email message, make sure the confirm link works
        body = mail.outbox[0].body
        lines = body.split('\n')
        for line in lines:
            if '/confirm' in line:
                link = line.strip()
                self.client.get(link)

                #reload subscriber
                subscriber = Subscriber.objects.get(email = 'name@place.com')

                self.assertEqual(subscriber.confirmed, True)

        #Verify that the subject of the message is correct.
        self.assertEqual(mail.outbox[0].subject, 
                          '[Tor Weather] Confirmation Needed')

    def test_subscribe_bad(self):
        """Make sure the form does not submit if a fingerprint is entered
        that isn't in the database."""
        response = self.client.post('/subscribe/', {'email_1':'name@place.com',
                                          'email_2':'name@place.com',
                                          'fingerprint' : '12345',
                                          'get_node_down' : True,
                                          'node_down_grace_pd' : '',
                                          'get_version' : True,
                                          'version_type' : 'UNRECOMMENDED',
                                          'get_band_low': True,
                                          'band_low_threshold' : '',
                                          'get_t_shirt' : True},
                                          follow = True)

        #we want to stay on the same page (the subscribe form)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template[0].name, 'subscribe.html')

        #Test that no messages have been sent
        time.sleep(3)
        self.assertEqual(len(mail.outbox), 0)
    
    def test_bandwidth_calc(self):
        """Make sure bandwidth arithmetic works. Averages should be calculated
        by rounding, not truncating."""
        ctl_util = CtlUtil()
        avg_bandwidth = 100
        hours_up = 1400
        current_bandwidth = 0
        new_avg = ctl_util.get_new_avg_bandwidth(avg_bandwidth, hours_up, 
                                                 current_bandwidth)
        self.assertEqual(new_avg, 100)
        
        avg_bandwidth = 10
        hours_up = 5
        current_bandwidth = 500
        new_avg = ctl_util.get_new_avg_bandwidth(avg_bandwidth, hours_up,
                                                 current_bandwidth)
        self.assertEqual(new_avg, 92)

    def test_earn_shirt(self):
        """Make sure checking conditions for earning a T-shirt works for 
        non-exit routers."""   
        #Create a non-exit router
        router = Router(fingerprint = '654', name='abc', exit=False)
        router.save()

        #Create a Subscriber
        subscriber = Subscriber(email = 'name@place.com', router = router) 
        subscriber.save()

        #Create a T-Shirt subscription following a router that's been running 
        #for 1464 hours, or 61 days (the minimum for earning a T-shirt)
        time_change = timedelta(61)
        then = datetime.now() - time_change
        shirt_sub = TShirtSub(subscriber = subscriber, avg_bandwidth = 500,
                              triggered = True, last_changed = then)
        shirt_sub.save()

        #Check to see that the email should be sent.
        hours_up = shirt_sub.get_hours_since_triggered()
        self.assertEqual(hours_up, 1464)
        self.assertEqual(shirt_sub.should_email(hours_up), True)

        #Make sure should_email is set to False if the bandwidth is too low
        shirt_sub.avg_bandwidth = 499
        self.assertEqual(shirt_sub.should_email(hours_up), False)

        #Make sure should_email is set to False if hours_up < 1464
        shirt_sub.avg_bandwidth = 500
        hours_up = 1463
        self.assertEqual(shirt_sub.should_email(hours_up), False)

    def test_earn_shirt_exit(self):
        """Make sure checking conditions for earning a T-shirt works for 
        exit routers."""
        #Create a router, set it to be an exit
        router = Router(fingerprint = '54321', name='abc', exit=True)
        router.save()

        #Create a Subscriber
        subscriber = Subscriber(email = 'name@place.com', router = router) 
        subscriber.save()

        #Create a T-Shirt subscription following a router that's been running 
        #for 1464 hours, or 61 days (the minimum for earning a T-shirt)
        time_change = timedelta(61)
        then = datetime.now() - time_change
        shirt_sub = TShirtSub(subscriber = subscriber, avg_bandwidth = 100,
                              triggered = True, last_changed = then)
        shirt_sub.save()

        #Check to see that the email should be sent.
        hours_up = shirt_sub.get_hours_since_triggered()
        self.assertEqual(hours_up, 1464)
        self.assertEqual(shirt_sub.should_email(hours_up), True)

        #Make sure should_email is set to False if the bandwidth is too low
        shirt_sub.avg_bandwidth = 99
        self.assertEqual(shirt_sub.should_email(hours_up), False)

        #Make sure should_email is set to False if hours_up < 1464
        shirt_sub.avg_bandwidth = 100
        hours_up = 1463
        self.assertEqual(shirt_sub.should_email(hours_up), False)
