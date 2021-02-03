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
from customer.pagination import LimitSkipPagination


# The ViewSet automatically handles API URLs
class PurchaseViewSet(viewsets.ModelViewSet):
    # API endpoint that returns the user's Purchases as an unsorted list of JSON objects
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    #permission_classes = [permissions.IsAuthenticated]
    pagination_class = LimitSkipPagination
    
    def list(self, request):
        queryset = Purchase.objects.all()
    
        # Get any query parameters
        options = self.request.query_params
        filterString = options.get('filterString', None)
        travel_valid_during_from = options.get('travel_valid_during_from', None)
        if not travel_valid_during_from:
            travel_valid_during_from = options.get('travel-valid-during-from', None)
        travel_valid_during_to = options.get('travel_valid_during_from', None)
        if not travel_valid_during_to:
            travel_valid_during_to = options.get('travel-valid-during-to', None)
        
        # Filter the queryset with the given parameters
        if filterString:
            queryset = queryset.filter(id__id__contains=filterString)
        if travel_valid_during_from:
            queryset = queryset.filter(travel_to_date_time__gte=travel_valid_during_from)
        if travel_valid_during_to:
            queryset = queryset.filter(travel_from_date_time__lte=travel_valid_during_to)
            
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
    #permission_classes = [permissions.IsAuthenticated]
    pagination_class = LimitSkipPagination
    
    def list(self, request):
        #queryset = Concession.objects.filter(customer__user=request.user)
        queryset = Concession.objects.all()

        # Get any query parameters
        options = self.request.query_params
        filterString = options.get('filterString', None)
        concession_valid_during_from = options.get('concession_valid_during_from', None)
        if not concession_valid_during_from:
            concession_valid_during_from = options.get('concession-valid-during-from', None)
        concession_valid_during_to = options.get('concession_valid_during_from', None)
        if not concession_valid_during_to:
            concession_valid_during_to = options.get('concession-valid-during-to', None)
        
        # Filter the queryset with the given parameters
        if filterString:
            queryset = queryset.filter(id__id__contains=filterString)
        if concession_valid_during_from:
            queryset = queryset.filter(valid_to_date_time__gte=concession_valid_during_from)
        if concession_valid_during_to:
            queryset = queryset.filter(valid_from_date_time__lte=concession_valid_during_to)
        
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
    #permission_classes = [permissions.IsAuthenticated]
    pagination_class = LimitSkipPagination
    
    def list(self, request):
        #queryset = Usage.objects.filter(customer__user=request.user)
        queryset = Usage.objects.all()

        # Get any query parameters
        options = self.request.query_params
        filterString = options.get('filterString', None)
        usage_occurred_during_from = options.get('usage_occurred_during_from', None)
        if not usage_occurred_during_from:
            usage_occurred_during_from = options.get('usage-occurred-during-from', None)
        usage_occurred_during_to = options.get('usage_occurred_during_from', None)
        if not usage_occurred_during_to:
            usage_occurred_during_to = options.get('usage-occurred-during-to', None)
        
        # Filter the queryset with the given parameters
        if filterString:
            queryset = queryset.filter(id__id__contains=filterString)
        if usage_occurred_during_from:
            queryset = queryset.filter(travel_to__date_time__gte=usage_occurred_during_from)
        if usage_occurred_during_to:
            queryset = queryset.filter(travel_from__date_time__lte=usage_occurred_during_to)
        
        
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
