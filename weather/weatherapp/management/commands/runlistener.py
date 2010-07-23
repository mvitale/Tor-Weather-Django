"""A Django command module to run weather/listener.py using
$ python manage.py runlistener
and automatically import the Django settings module for use
by it."""

from weatherapp import listener

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    """Represents a Django manage.py command to run listener.py
    
    @type help: str
    @cvar help: Help text for the command"""

    help = 'Run listener.py with correct Django settings'

    def handle(self, *args, **options):
        """Called when runlistener is called from the command line. Starts
        the listener."""
        listener.listen()
