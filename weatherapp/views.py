from django.shortcuts import render_to_response, get_object_or_404
from weather.weatherapp.models import Subscriber, Subscription
from django.core.mail import send_mail 
import weather.weatherapp.emails
from weather.weatherapp.models import Emailer, CheckSubscriptions

# -----------------------------------------------------------------------
# FILL IN ONCE WE KNOW THE SITE! ----------------------------------------
# -----------------------------------------------------------------------
baseURL = "localhost:8000"

def subscribe(request):
    if request.method == 'POST'
        form = SubscribeForm(request.POST)

# -----------------------------------------------------------------------
# NEED TO CHECK HOW DJANGO CHECKS IF AN EMAIL FIELD IS VALID ------------
# -----------------------------------------------------------------------
        if form.is_valid():
            addr = form.cleaned_data['email']
            fingerprint = form.cleaned_data['router_id']
            grace_pd = form.cleaned_data['grace_pd']
            
            Emailer.send_confirmation_mail(addr)

            # Add subscriber to the database
            subscriber = Subscriber.add_new_subscriber() 

            
            return HttpResponseRedirect('/pending/'+subscriber.id+'/')
    else:
        form = SubscribeForm()
    return render_to_response('subscribe.html', {'form': form,})

def pending(request, subscriber_id):
    suber = get_object_or_404(Subscriber, pk=subscriber_id)
    return render_to_response('pending.html', {'email': sub.email})

def confirm(request, confirm_auth_id):
    subscriber = get_object
    sub = get_object_or_404(Subscriber, confirm_auth=confirm_auth_id)
    rout = Router.objects.get(pk=sub.router_id)
    unsubURL = baseURL + "/unsubscribe/" + suber.unsubs_auth + "/"
    prefURL = baseURL + "/preferences/" + suber.pref_auth + "/"
    return render_to_response('confirm.html', {'email': sub.email, \
            'fingerprint' : rout.fingerprint, 'nodeName' : rout.name, \
            'unsubURL' : unsubURL, 'prefURL' : prefURL})
        
def unsubscribe(request, unsubscribe_auth_id):
    return render_to_response('unsubscribe.html')

# -------------------------------------------------------------------------
# Changing preferences isn't in the base functionality, will worry later.
# Needs to check each subscription belonging to a subscriber, and then
# pass through the name and threshold for each of the subscriptions, along
# with a boolean representing that that type of notification is on.
# Then will need to pass through the name and threshold for each type
# of notification not subscribed to, along with a boolean representing that
# the notification is off.
# THIS IS PLACEHOLDER CODE, YO!
def preferences(request, preferences_auth_id):
   return HttpResponse("dude your preferences code is %s." \
           % preferences_auth_id)
# -------------------------------------------------------------------------

def runpoller(request):
    # ---------------------------------------------------------------------
    # here is where we need to have code that calls the necessary stuff in
    # models to run stuff throughout the life of the application
    # ---------------------------------------------------------------------
    client_ip = request.META['HTTP_X_FORWARDED_FOR'] 

    #only allow requests from localhost
    if client_ip == '127.0.0.1':
       checker = CheckSubscriptions() 
       checker.check_all()
    else:
        raise Http404
    return
