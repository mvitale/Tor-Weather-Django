"""A module for listening to TorCtl for new consensus events. When one occurs,
initializes the checker/updater cascade in the updaters module."""

import sys, os
import logging
import socket

from config import config
from weatherapp import updaters
from TorCtl import TorCtl

#very basic log setup
logging.basicConfig(format = '%(asctime) - 15s (%(process)d) %(message)s',
                    level = logging.DEBUG, filename = 'log/weather.log')

class MyEventHandler(TorCtl.EventHandler):
    def new_consensus_event(self, event):
        logging.info('Got a new consensus. Updating router table and ' + \
                     'checking all subscriptions.')
        updaters.run_all()

def listen():
    """Sets up a connection to TorCtl and launches a thread to listen for
    new consensus events.
    """
    ctrl_host = "127.0.0.1"
    ctrl_port = 9055
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ctrl_host, ctrl_port))
    ctrl = TorCtl.Connection(sock)
    ctrl.launch_thread(daemon=0)
    ctrl.authenticate(config.authenticator)
    ctrl.set_event_handler(MyEventHandler())
    ctrl.set_events([TorCtl.EVENT_TYPE.NEWCONSENSUS])
    print 'Listening for new consensus events.'
    logging.info('Listening for new consensus events.')

def run_updaters():#just for testing
    updaters.run_all()
