from django.shortcuts import render_to_response, get_object_or_404
from weather.weatherapp.models import Subscriber

#FILL IN ONCE WE KNOW THE SITE!
baseURL = "localhost:8000"

def subscribe(request):
    return render_to_response('subscribe.html')

def pending(request):
    sub = get_object_or_404(Subscriber, pk=subscriber_id)
    return render_to_response('pending.html', {'email': sub.email})

def confirm(request, confirm_auth_id):
    sub = get_object_or_404(Subscriber, confirm_auth=confirm_auth_id)
    rout = Router.objects.get(pk=sub.router_id)
    unsubURL = baseURL + "/unsubscribe/" + sub.unsubs_auth + "/"
    prefURL = baseURL + "/preferences/" + sub.pref_auth + "/"
    return render_to_response('confirm.html', {'email': sub.email, \
            'fingerprint' : rout.fingerprint, 'nodeName' : rout.name, \
            'unsubURL' : unsubURL, 'prefURL' : prefURL})
        
def unsubscribe(request, unsubscribe_auth_id):
    return HttpResponse("dude your unsubscribe code is %s." \
            % unsubscribe_auth_id)

def preferences(request, preferences_auth_id):
    return HttpResponse("dude your preferences code is %s." \
            % preferences_auth_id)

