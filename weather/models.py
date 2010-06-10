from django.db import models
import datetime.date

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

class Subscriber(models.Model)
    email = models.EmailField(max_length=75)
    router_id = models.ForeignKey(Router)

    #change this when more is known
    subs_auth = models.CharField(max_length=300) 
    unsubs_auth = models.CharField(max_length=300)
    pref_auth = models.CharField(max_length=300)

    sub_date = models.DateField()



