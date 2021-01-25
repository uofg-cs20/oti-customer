from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Mode, Purchase, Concession, Usage
from .helper_functions import getDates, getModes, formatDate, getPurchases, getConcessions, getUsage, getOperators
from datetime import date
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .serializers import PurchaseSerializer, ConcessionSerializer, UsageSerializer
from .forms import LoginForm


# The ViewSet automatically handles API URLs
class PurchaseViewSet(viewsets.ModelViewSet):
    # API endpoint that returns the user's Purchases as an unsorted list of JSON objects
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        filterString = self.request.query_params.get('filterString', None)
        queryset = Purchase.objects.filter(customer__user=request.user)
        if filterString:
            queryset = queryset.filter(id__id__contains=filterString)            
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PurchaseSerializer(page, many=True)
        else:
            serializer = PurchaseSerializer(queryset, many=True)
        return Response(serializer.data)
    
    
class ConcessionViewSet(viewsets.ModelViewSet):
    # API endpoint that returns the user's Concessions as an unsorted list of JSON objects
    queryset = Concession.objects.all()
    serializer_class = ConcessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        queryset = Concession.objects.filter(customer__user=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ConcessionSerializer(page, many=True)
        else:
            serializer = ConcessionSerializer(queryset, many=True)
        return Response(serializer.data)
    
    
class UsageViewSet(viewsets.ModelViewSet):
    # API endpoint that returns the user's Usages as an unsorted list of JSON objects
    queryset = Usage.objects.all()
    serializer_class = UsageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        queryset = Usage.objects.filter(customer__user=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UsageSerializer(page, many=True)
        else:
            serializer = UsageSerializer(queryset, many=True)
        return Response(serializer.data)

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
    operators = getOperators()
    context = {"operators": operators}
    return render(request, 'website/connect.html', context)


def purchases(request):
    context = {"purchases":[], "modes":[]}
    context["modes"] = getModes()
    startdate, enddate = getDates(request)
    mode = request.POST.get("mode")

    context['startdate'] = startdate
    context['enddate'] = enddate
        
    if mode and mode != "None":
        context.update({"mode":mode})

    # Retrieve a list of Purchases filtered by the given fields in the context dictionary
    context["purchases"] = getPurchases(request.user, context)

    return render(request, 'website/purchases.html', context)


def concessions(request):
    context = {}
    context["expired"] = False
    context["modes"] = getModes()

    if request.method == "POST":
        status = request.POST.get("status")
        mode = request.POST.get("mode")

        # check if the customer wants to see expired concessions
        if status == 'past':
            context['expired'] = True

        if mode and mode != "None":
            context["mode"] = mode

    # obtain either current or past concessions for user 
    concessions = getConcessions(request.user, context)
    context['concessions'] = concessions

    return render(request, 'website/concessions.html', context)


def usage(request):
    context = {}
    context["modes"] = getModes()
    startdate, enddate = getDates(request)
    mode = request.POST.get("mode")

    context['startdate'] = startdate
    context['enddate'] = enddate
    context['mode'] = mode

    usages = getUsage(request.user, context)
    context['usages'] = usages
    
    return render(request, 'website/usage.html', context)   