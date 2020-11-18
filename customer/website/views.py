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
    context = {"purchases":[], "modes":Mode.objects.all()}
    
    if request.method == "POST":
        startdatestr = request.POST.get("startdate")
        enddatestr = request.POST.get("enddate")
        mode = request.POST.get("mode")
        if startdatestr:
            startdate = formatDate(startdatestr)
            context.update({"startdate":startdate})
        if enddatestr:
            enddate = formatDate(enddatestr)
            context.update({"enddate":enddate})
        if mode:
            context.update({"mode":mode})
    
    purchases = getPurchases(request.user, context)
        
    for p in purchases:
        context["purchases"].append(p)
        
    return render(request, 'website/purchases.html', context)

def concessions(request):
    # TODO
    return render(request, 'website/concessions.html')

def usage(request):
    # TODO
    return render(request, 'website/usage.html')
