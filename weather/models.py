from django.db import models
import datetime.date

# Create your models here.
class Subscriber(models.Model)
    email = models.EmailField(max_length=75)
    router_id = models.ForeignKey(Router)

    #change this when more is known
    subs_auth = models.CharField(max_length=250) 
    unsubs_auth = models.CharField(max_length=250)
    pref_auth = models.CharField(max_length=250)

    sub_date = models.DateField()
