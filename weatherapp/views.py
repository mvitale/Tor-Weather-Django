from django.http import HttpResponse

def subscribe(request):
    return HttpResponse("Dude this is a form")

def pending(request):
    return HttpResponse("dude this is pending")

def confirm(request, confirm_auth_id):
    return HttpResponse("dude your confirm code is %s." % confirm_auth_id)

def unsubscribe(request, unsubscribe_auth_id):
    return HttpResponse("dude your unsubscribe code is %s." \
            % unsubscribe_auth_id)

def preferences(request, preferences_auth_id):
    return HttpResponse("dude your preferences code is %s." \
            % preferences_auth_id)

