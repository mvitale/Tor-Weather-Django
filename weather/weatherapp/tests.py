"""
The test module.
"""
from models import Subscriber, Subscription, Router, NodeDownSub

from django.test import TestCase
from django.test.client import Client
from django.core import mail

class WebTests(TestCase)
    """Tests the Tor Weather application via post requests"""
    def subscribe_test(self)
        c = Client()
        r = Router(fingerprint = '1234', name = 'abc')
        r.save()
        response = c.post('/subscribe/', {'email' : 'name@place.com',
                                          'fingerprint' : '1234', 
                                          'grace_pd' : 1})

 
