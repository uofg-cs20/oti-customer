from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import logout

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
    # TODO
    return render(request, 'website/purchases.html')

def concessions(request):
    # TODO
    return render(request, 'website/concessions.html')

def usage(request):
    # TODO
    return render(request, 'website/usage.html')
