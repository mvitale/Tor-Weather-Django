"""
The test module. To run tests, cd to weather and run 'python manage.py
test weatherapp'.
"""
from models import Subscriber, Subscription, Router, NodeDownSub, TShirtSub,\
                   VersionSub, BandwidthSub

from django.test import TestCase
from django.test.client import Client
from django.core import mail

class TestWeb(TestCase):
    """Tests the Tor Weather application via post requests"""

    def setUp(self):
        """Set up the test database with a dummy router"""
        r = Router(fingerprint = '1234', name = 'abc')
        r.save()

    def test_subscribe_node_down(self):
        """Test a node down subscription (all other subscriptions off)"""
        c = Client()
        response = c.post('/subscribe/', {'email_1' : 'name@place.com',
                                          'email_2' : 'name@place.com',
                                          'fingerprint' : '1234',
                                          'get_node_down' : True,
                                          'node_down_grace_pd' : 1,
                                          'get_out_of_date' : False,
                                          'get_band_low': False,
                                          'get_t_shirt' : False},
                                          follow = True)
        #we want to be redirected to the pending page
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template[0].name, 'pending.html')

        subscriber = Subscriber.objects.get(email = 'name@place.com')
        self.assertEqual(subscriber.email, 'name@place.com')
        self.assertEqual(subscriber.router.fingerprint, '1234')
        self.assertEqual(subscriber.confirmed, False)
        
        # there should only be one subscription for this subscriber
        subscription_list = Subscription.objects.filter(subscriber = subscriber)
        self.assertEqual(len(subscription_list), 1)
        node_down_sub = NodeDownSub.objects.get(subscriber = subscriber)
        self.assertEqual(node_down_sub.emailed, False)
        self.assertEqual(node_down_sub.triggered, False)
        self.assertEqual(node_down_sub.grace_pd, 1)
    
    def test_subscribe_version(self):
        """Test a version subscription (all other subscriptions off)"""
        c = Client()
        response = c.post('/subscribe/', {'email_1' : 'name@place.com',
                                          'email_2' : 'name@place.com',
                                          'fingerprint' : '1234',
                                          'get_node_down' : False,
                                          'get_out_of_date' : True,
                                          'out_of_date_threshold' : 'c1',
                                          'get_band_low': False,
                                          'get_t_shirt' : False},
                                          follow = True)
        #we want to be redirected to the pending page
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template[0].name, 'pending.html')

        subscriber = Subscriber.objects.get(email = 'name@place.com')
        self.assertEqual(subscriber.email, 'name@place.com')
        self.assertEqual(subscriber.router.fingerprint, '1234')
        self.assertEqual(subscriber.confirmed, False)
        
        # there should only be one subscription for this subscriber
        subscription_list = Subscription.objects.filter(subscriber = subscriber)
        self.assertEqual(len(subscription_list), 1)
        version_sub = VersionSub.objects.get(subscriber = subscriber)
        self.assertEqual(version_sub.emailed, False)

# --------- CONFIGURE VERSION TYPE -----------------------------------
        ##self.assertEqual(version_sub.notify_type, '')
    
    def test_subscribe_bandwidth(self):
        """Test a bandwidth only subscription attempt"""
        c = Client()
        r = Router(fingerprint = '1234', name = 'abc')
        r.save()
        response = c.post('/subscribe/', {'email1' : 'name@place.com',
                                          'email2': 'name@place.com',
                                          'fingerprint' : '1234', 
                                          'get_node_down': False,
                                          'get_out_of_date' : False,
                                          'get_band_low' : True,
                                          'band_low_threshold' : 20,
                                          'band_low_grace_pd' : 2,
                                          'get_t_shirt' : False})
        #we want to be redirected to the pending page
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template[0].name, 'pending.html')

        subscriber = Subscriber.objects.get(email = 'name@place.com')
        self.assertEqual(subscriber.email, 'name@place.com')
        self.assertEqual(subscriber.router.fingerprint, '1234')
        self.assertEqual(subscriber.confirmed, False)

    def test_subscribe_all(self):
        """Test a subscribe attempt to all subscription types, relying
        on default values."""
        c = Client()
        response = c.post('/subscribe/', {'email_1' : 'name@place.com',
                                          'email_2' : 'name@place.com',
                                          'fingerprint' : '1234',
                                          'get_node_down' : True,
                                          'get_out_of_date' : True,
                                          'out_of_date_threshold' : 'c1',
                                          'get_band_low': True,
                                          'get_t_shirt' : True},
                                          follow = True)
        print response
        #we want to be redirected to the pending page
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template[0].name, 'pending.html')

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
        #self.assertEqual(version.notify_type,

        bandwidth = BandwidthSub.objects.get(subscriber = subscriber)
        self.assertEqual(bandwidth.triggered, False)
        self.assertEqual(bandwidth.emailed, False)
        self.assertEqual(bandwidth.grace_pd, 1)
        self.assertEqual(bandwidth.threshold, 20)
        
        tshirt = TShirtSub.objects.get(subscriber = subscriber)
        self.assertEqual(tshirt.avg_bandwidth, 0)
        self.assertEqual(tshirt.emailed, False)

    def test_subscribe_bad(self):
        c = Client()
        response = c.post('/subscribe/', {'email' : 'name@place.com',
                                          'fingerprint' : '12345'})
        #we want to stay on the same page (the subscribe form)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template[0].name, 'subscribe.html')
