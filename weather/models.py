from django.db import models
import datetime.date

# Create your models here.
class Subscriber(models.Model)
    email = models.EmailField(max_length=75)
    router_id = models.ForeignKey(Router)

    #change this when more is known
    subs_auth = models.CharField(max_length=300) 
    unsubs_auth = models.CharField(max_length=300)
    pref_auth = models.CharField(max_length=300)

    sub_date = models.DateField()

class Router(models.Model)
    finger = models
