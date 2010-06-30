"""
The test module. To run tests, cd to weather and run 'python manage.py
test weatherapp'.
"""
from models import Subscriber, Subscription, Router, NodeDownSub, TShirtSub

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
        response = c.post('/subscribe/', {'email_1' : 'name@place.com',
                                          'email_2': 'name@place.com',
                                          'fingerprint' : '1234', 
                                          'get_node_down' : True,
                                          'node_down_grace_pd' : 1,
                                          'get_out_of_date' : False,
                                          'get_band_low' : False,
                                          'get_t_shirt' : False},
                                          follow = True)#set follow to True
                                                        #to follow redirects

        #we want to be redirected to the pending page
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template[0].name, 'pending.html')

        #Test that one message has been sent
        self.assertEquals(len(mail.outbox), 1)

        #Verify that the subject of the message is correct.
        self.assertEquals(mail.outbox[0].subject, 
                          '[Tor Weather] Confirmation Needed')

    def test_subscribe_bandwidth(self):
        """Test a bandwidth only subscription attempt"""
        c = Client()
        r = Router(fingerprint = '1234', name = 'abc')
        r.save()
        response = c.post('/subscribe/', {'email_1' : 'name@place.com',
                                          'email_2': 'name@place.com',
                                          'fingerprint' : '1234', 
                                          'get_node_down': False,
                                          'get_out_of_date' : False,
                                          'get_band_low' : True,
                                          'band_low_threshold' : 20,
                                          'band_low_grace_pd' : 2,
                                          'get_t_shirt' : False},
                                          follow = True)
                                          
        #We want to be redirected to the pending page
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template[0].name, 'pending.html')
        
        #Test that one message has been sent
        self.assertEquals(len(mail.outbox), 1)

        #Verify that the subject of the message is correct.
        self.assertEquals(mail.outbox[0].subject, 
                          '[Tor Weather] Confirmation Needed')

    def test_subscribe_bad(self):
        c = Client()
        response = c.post('/subscribe/', {'email' : 'name@place.com',
                                          'fingerprint' : '12345'})
        #we want to stay on the same page (the subscribe form)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template[0].name, 'subscribe.html')

        #Test that no messages have been sent
        self.assertEquals(len(mail.outbox), 0)
