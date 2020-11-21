from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Mode, Purchase, Concession, Usage
<<<<<<< HEAD
from .helper_functions import getModes, formatDate, getPurchases, getConcessions
=======
from .helper_functions import getModes, formatDate, getPurchases
>>>>>>> master
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
    return redirect(reverse('website:login'))

def connect(request):
    # TODO
    return render(request, 'website/connect.html')

def purchases(request):
    # Initialise a context dictionary to store the Purchases and available
    # modes of transport
    context = {"purchases":[], "modes":[]}
    context["modes"] = getModes()

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
    context["purchases"] = getPurchases(request.user, context)

    return render(request, 'website/purchases.html', context)

def concessions(request):
    context = {"status" : " "}
    if request.method == "POST":
        status = request.POST.get("status")
        # expired concession status selected
        if status == "past":
            status = None
        context['status'] = status

    # use helper function to obtain relevant concessions for user
    # depending on whether current or past concessions are requested
    concessions = getConcessions(request.user, context)
    context['concessions'] = []
    # iterate over obtained concessions and add to context dict
    for c in concessions:
        context['concessions'].append(c)

    return render(request, 'website/concessions.html', context)

def usage(request):
    # TODO
    return render(request, 'website/usage.html')
