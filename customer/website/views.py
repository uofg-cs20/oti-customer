from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Mode, Purchase, Concession, Usage
from .helper_functions import formatDate, getPurchases, getUsage
from datetime import date

from .forms import LoginForm


def index(request):
    return render(request, 'website/index.html')

def register(request):
    # TODO
    return render(request, 'website/register.html')

def customer_login(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            loginName = form.cleaned_data['username']
            loginPass = form.cleaned_data['password']

            user = authenticate(username = loginName, password = loginPass)
            login(request, user)

            return redirect(reverse('website:purchases'))

    return render(request, 'website/login.html', {"form": form})

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
    # TODO
    return render(request, 'website/concessions.html')

def usage(request):
    usages = getUsage(request.user)
    context = {}
    if not usages:
        context['valid'] = False
    else:
        context = {"modes": Mode.objects.all(), "combined_tickets": usages}
    return render(request, 'website/usage.html', context)
