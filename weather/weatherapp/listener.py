"""A module for listening to TorCtl for new consensus events. When one occurs,
initializes the checker/updater cascade in the updaters module."""

import sys, os
import logging
import socket

from weather.weatherapp import config, updaters
from weather import settings
from TorCtl import TorCtl

from django.core.management import setup_environ

setup_environ(settings)
sys.path.append(os.path.abspath('../..'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'weather.settings'

#very basic log setup
logging.basicConfig(format = '%(asctime) - 15s (%(process)d) %(message)s',
                    level = logging.INFO, filename = './weather.log')

class MyEventHandler(TorCtl.EventHandler):
    def new_consensus_event(self, event):
        updaters.run_all()

def main():
    """Sets up a connection to TorCtl and launches a thread to listen for
    new consensus events.
    """
    ctrl_host = "127.0.0.1"
    ctrl_port = 9051
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ctrl_host, ctrl_port))
    ctrl = TorCtl.Connection(sock)
    ctrl.launch_thread(daemon=0)
    ctrl.authenticate(config.authenticator)
    ctrl.set_event_handler(MyEventHandler())
    ctrl.set_events([TorCtl.EVENT_TYPE.NEWCONSENSUS])

def run_updaters():#just for testing
    updaters.run_all()

if __name__ == '__main__':
    run_updaters()
    #main()
