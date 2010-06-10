from django.db import models

class Subscription(models.Model):
    subscriber_id = models.ForeignKey(Subscriber)
    name = models.CharField(max_length=200)
    threshold = models.CharField(max_length=200)
    grace_pd = models.IntegerField()
    emailed = models.BooleanField()
    triggered = models.BooleanField()
    last_changed = models.DateTimeField('date of last change')

    def __unicode__(self):
        return self.name

class Router(models.Model):
    fingerprint = models.CharField(max_length=200)
    welcomed = models.BooleanField()
    last_seen = models.DateTimeField('date last seen')
