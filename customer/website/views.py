from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import logout
from .models import Mode, Purchase, Concession, Usage
from .helper_functions import formatDate, getPurchases
from datetime import date

def index(request):
    return render(request, 'website/index.html')

def register(request):
    # TODO
    return render(request, 'website/register.html')

def customer_login(request):
    # TODO
    return render(request, 'website/login.html')

def customer_logout(request):
    logout(request)
    return redirect(reverse('website:index'))

def connect(request):
    # TODO
    return render(request, 'website/connect.html')

def purchases(request):
    # Initialise a context dictionary to store the Purchases and available
    # modes of transport
    context = {"purchases":[], "modes":Mode.objects.all()}
    
    if request.method == "POST":
        # Check if filters have been applied, store these in the
        # context dictionary to process
        startdatestr = request.POST.get("startdate")
        enddatestr = request.POST.get("enddate")
        mode = request.POST.get("mode")
        if startdatestr:
            startdate = formatDate(startdatestr)
            context.update({"startdate":startdate})
        if enddatestr:
            enddate = formatDate(enddatestr)
            context.update({"enddate":enddate})
        if mode and mode != "None":
            context.update({"mode":mode})
    
    # Retrieve a list of Purchases filtered by the given fields in
    # the context dictionary, and store these in the context dictionary
    purchases = getPurchases(request.user, context)
    for p in purchases:
        context["purchases"].append(p)
        
    return render(request, 'website/purchases.html', context)

def concessions(request):
    
    context = {}
    if request.method == "POST":
        status = request.POST.get("status")
        # if no concession status selected,  will return valid ones only
        if not status:
            status = "valid"
        context['status'] = status

    # use helper function to obtain relevant concessions for user
    # depending on whether current or past concessions are requested
    concessions = getConcessions(request.user, status)
    context['concessions'] = []
    # iterate over obtained concessions and add to context dict
    for c in concessions:
        context['concessions'].append(c)

    return render(request, 'website/concessions.html', context)

def usage(request):
    # TODO
    return render(request, 'website/usage.html')
