from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Mode, Purchase, Concession, Usage
from .helper_functions import getModes, formatDate, getPurchases, getConcessions, getUsage
from datetime import date
from rest_framework import viewsets
from rest_framework import permissions
from .serializers import PurchaseSerializer, ConcessionSerializer, UsageSerializer
from .forms import LoginForm


# The ViewSet automatically handles API URLs
class PurchaseViewSet(viewsets.ModelViewSet):
    # API endpoint that allows Purchases to be viewed or edited.
    queryset = Purchase.objects.all().order_by('-travel_to_date_time')
    serializer_class = PurchaseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
class ConcessionViewSet(viewsets.ModelViewSet):
    # API endpoint that allows Concessions to be viewed or edited.
    queryset = Concession.objects.all().order_by('-valid_to_date_time')
    serializer_class = ConcessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
class UsageViewSet(viewsets.ModelViewSet):
    # API endpoint that allows Usages to be viewed or edited.
    queryset = Usage.objects.all().order_by('mode')
    serializer_class = UsageSerializer
    permission_classes = [permissions.IsAuthenticated]

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
            # If startdate was provided and is greater than the enddate, switch them
            s = context.get("startdate")
            if s:
                if s > enddate:
                    context.update({"startdate":enddate})
                    context.update({"enddate":s})
        if mode and mode != "None":
            context.update({"mode":mode})

    # Retrieve a list of Purchases filtered by the given fields in
    # the context dictionary, and store these in the context dictionary
    context["purchases"] = getPurchases(request.user, context)

    return render(request, 'website/purchases.html', context)

def concessions(request):
    context = {}
    context["status"] = "valid"
    context["modes"] = getModes()
    if request.method == "POST":

        status = request.POST.get("status")
        mode = request.POST.get("mode")
        # if no status selected, will examine valid concessions
        if status == None:
            status = "valid"
        # expired concession status selected
        if status == "past":
            status = None
        context["status"] = status
        if mode and mode != "None":
            context["mode"] = mode

    # use helper function to obtain relevant concessions for user
    # depending on whether current or past concessions are requested
    concessions = getConcessions(request.user, context)
    print(concessions)
    context['concessions'] = []
    # iterate over obtained concessions and add to context dict
    for c in concessions:
        context['concessions'].append(c)

    return render(request, 'website/concessions.html', context)

def usage(request):
    context = {}
    context["modes"] = getModes()
    mode = ""
    if request.method == "POST":
        # Check if filters have been applied, store these in the
        # context dictionary to process
        startdate, enddate = "", ""
        startdatestr = request.POST.get("startdate")
        enddatestr = request.POST.get("enddate")
        mode = request.POST.get("mode")
        if startdatestr:
            startdate = formatDate(startdatestr)
        if enddatestr:
            enddate = formatDate(enddatestr)
    else:
        startdate, enddate = "", ""
    usages = getUsage(request.user, [startdate, enddate, mode])
    if not usages:
        context['valid'] = False
    else:
        context['combined_tickets'] = usages
    return render(request, 'website/usage.html', context)
