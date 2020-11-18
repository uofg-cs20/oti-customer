from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import logout
from .models import Purchase, Concession, Usage
from .helper_functions import formatDate, getPurchases
from .forms import FilterTickets
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
    context = {"purchases":[]}
    
    if request.method == "POST":
        form = FilterTickets(request.POST)
        if form.is_valid():
            startdatestr = form.cleaned_data["startdate"]
            enddatestr = form.cleaned_data["enddate"]
            purchases = getPurchases(request.user, formatDate(startdatestr), formatDate(enddatestr))
            context.update({"form":form})
        else:
            purchases = getPurchases(request.user)
    else:
        purchases = getPurchases(request.user)
        
    for p in purchases:
        context["purchases"].append(p)
        
    return render(request, 'website/purchases.html', context)

def concessions(request):
    # TODO
    return render(request, 'website/concessions.html')

def usage(request):
    # TODO
    return render(request, 'website/usage.html')
