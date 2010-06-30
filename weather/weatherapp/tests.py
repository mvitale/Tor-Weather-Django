"""
The test module.
"""
from models import Subscriber, Subscription, Router, NodeDownSub

from django.test import TestCase
from django.test.client import Client
from django.core import mail

class TestWeb(TestCase):
    """Tests the Tor Weather application via post requests"""
    def test_subscribe(self):
        c = Client()
        r = Router(fingerprint = '1234', name = 'abc')
        r.save()
        response = c.post('/subscribe/', {'email' : 'name@place.com',
                                          'fingerprint' : '1234', 
                                          'grace_pd' : 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template[0].name, 'pending.html')
    def test_subscribe_bad(self):
        c = Client()
        response = c.post('/subscribe/', {'email' : 'name@place.com',
                                          'fingerprint' : '12345'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template[0].name, 'subscribe.html')
