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
    """Extends C{TorCtl.EventHandler} so that C{updaters.run_all} is called
    when a NEWCONSENSUS event is received.
    """
    def new_consensus_event(self, event):
        """Call C{updaters.run_all()} when a NEWCONSENSUS event is received.

        @param event: The NEWCONSENSUS event. Not used by the function,
                      but included so that this overrides 
                      C{TorCtl.EventHandler.new_consensus_event}
        """

        logging.info('Got a new consensus. Updating router table and ' + \
                     'checking all subscriptions.')
        updaters.run_all()

def listen():
    """Sets up a connection to TorCtl and launches a thread to listen for
    new consensus events.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ctrl_host = '127.0.0.1'
    ctrl_port = config.control_port
    sock.connect((ctrl_host, ctrl_port))
    ctrl = TorCtl.Connection(sock)
    ctrl.launch_thread(daemon=0)
    ctrl.authenticate(config.authenticator)
    ctrl.set_event_handler(MyEventHandler())
    ctrl.set_events([TorCtl.EVENT_TYPE.NEWCONSENSUS])
    print 'Listening for new consensus events.'
    logging.info('Listening for new consensus events.')

