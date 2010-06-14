from django.shortcuts import render_to_response, get_object_or_404
from weather.weatherapp.models import Subscriber, Subscription
from django.core.mail import send_mail 
from weather.weatherapp.emails
from weather.weatherapp.models import Emailer

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
    sub = get_object_or_404(Subscriber, confirm_auth=confirm_auth_id)
    rout = Router.objects.get(pk=sub.router_id)
    unsubURL = baseURL + "/unsubscribe/" + suber.unsubs_auth + "/"
    prefURL = baseURL + "/preferences/" + suber.pref_auth + "/"
    return render_to_response('confirm.html', {'email': sub.email, 
            'fingerprint' : rout.fingerprint, 'nodeName' : rout.name, 
            'unsubURL' : unsubURL, 'prefURL' : prefURL})
        
def unsubscribe(request, unsubscribe_auth_id):
    """The unsubscribe page"""
    
    #get the user and router
    user = get_object_or_404(Subscriber, unsubs_auth = unsubscribe_auth_id)
    router = get_object_or_404(Router, id = user.router)
    
    email = user.email
    router_name = router.name
    fingerprint = router.fingerprint 
    
    #we know the router has a fingerprint, but it might not have a name.
    name = ""
    if !router_name.equals("Unnamed"):
        name += " " + router_name + ","

    return render_to_response('unsubscribe.html'{'email' : email, 'name' :
            name, 'fingerprint' : fingerprint})

def preferences(request, preferences_auth_id):
    """The preferences page"""
    if request.method == "POST":
        form = PreferencesForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('confirm_pref/'+preferences_auth_id+'/',
                    preferences_auth_id) 
    else:
        user = get_object_or_404(Subscriber, pref_auth = preferences_auth_id)
        node_down_sub = get_object_or_404(Subscription, subscriber = user, 
                    name = node_down)
    
        # the data here should be expanded as the preferences are changed
        data = {'grace_pd' : node_down_sub.grace_pd}
        form = PreferencesForm(data)
    return render_to_response('preferences.html', {'form' : form})

def confirm_pref(request, preferences_auth_id)
    """The page confirming that preferences have been changed."""
    prefURL = baseURL + '/preferences/' + preferences_auth_id + '/'
    user = get_object_or_404(Subscriber, pref_auth = preferences_auth_id)
    unsubURL = baseURL + '/unsubscribe/' + user.unsub_auth + '/'
    return render_to_response('confirm_pref.html', {'prefURL' : prefURL,
            'unsubURL' : unsubURL})

def runpoller(request):
    # ---------------------------------------------------------------------
    # here is where we need to have code that calls the necessary stuff in
    # models to run stuff throughout the life of the application
    # ---------------------------------------------------------------------
