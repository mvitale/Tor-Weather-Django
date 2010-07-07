"""A Django command module to run weather/listener.py using
$ python manage.py runlistener
and automatically import the Django settings module for use
by it."""

import listener

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    """Represents a Django manage.py command to run listener.py"""
    help = 'Run listener.py with correct Django settings'

    def handle(self, *args, **options):
        listener.listen()
