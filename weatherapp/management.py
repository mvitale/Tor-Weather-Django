from django.dispatch import dispatcher
from django.db.models import signals
from weather.weatherapp import models
import subprocess

#def init_poller():
    #subprocess.Popen(['python', 'poller.py'])

#dispatcher.connect(init_poller, sender=models, signal=signals.post_syncdb)
