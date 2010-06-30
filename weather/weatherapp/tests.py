"""
The test module. To run tests, cd to weather and run 'python manage.py
test weatherapp'.
"""
from models import Subscriber, Subscription, Router, NodeDownSub

from django.test import TestCase
from django.test.client import Client
from django.core import mail

class TestWeb(TestCase):
    """Tests the Tor Weather application via post requests"""
    def test_subscribe_node_down(self):
        """Test a node down only subscription attempt"""
        c = Client()
        r = Router(fingerprint = '1234', name = 'abc')
        r.save()
        response = c.post('/subscribe/', {'email1' : 'name@place.com',
                                          'email2': 'name@place.com',
                                          'fingerprint' : '1234', 
                                          'get_node_down' : True,
                                          'node_down_grace_pd' : 1,
                                          'get_out_of_date' : False,
                                          'get_band_low' : False,
                                          'get_t_shirt' : False,})

        #we want to be redirected to the pending page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.template[0].name, 'pending.html')

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

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template[0].name, 'pending.html')



    def test_subscribe_bad(self):
        c = Client()
        response = c.post('/subscribe/', {'email' : 'name@place.com',
                                          'fingerprint' : '12345'})
        #we want to stay on the same page (the subscribe form)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template[0].name, 'subscribe.html')
