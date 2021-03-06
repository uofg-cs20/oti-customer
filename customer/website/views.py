from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.messages import success
from .models import Operator, Mode, Purchase, Concession, Usage, ConnectedAccount, Customer
from .linking_functions import getModes, getPurchases, getConcessions, getUsage, getOperators
from .helper_functions import getDates, generateTicketHeading
from datetime import date, timedelta
from django.utils import timezone
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .serializers import PurchaseSerializer, ConcessionSerializer, UsageSerializer
from .forms import LoginForm, RegisterForm
from customer.pagination import LimitSkipPagination
from customer.renderers import CustomJSONRenderer
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
import requests, json
from requests.auth import HTTPBasicAuth
from django.core.paginator import Paginator

client_id = "ou9h2JlNWlch0Vj7N2AzK6qYANdNIl1Mo7gg1oZj"
client_secret = "5EUIoebBH2SxgjANJ6KL1q1GcGZn924OCQbhbysqQ9kb79W3i9YBDGbMGlYw1NPee40fI3t0OYFW2zaghGl5buKfUzGQc7XuibqpbA296LKNiWWuF02RUUBaDAydV7t9"


# The ViewSet automatically handles API URLs
class PurchaseViewSet(viewsets.ModelViewSet):
    # API endpoint that returns the user's Purchases as an unsorted list of JSON objects
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LimitSkipPagination
    renderer_classes = [CustomJSONRenderer, BrowsableAPIRenderer, JSONRenderer]
    
    def list(self, request):
        queryset = Purchase.objects.filter(customer__user=request.user)
    
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
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LimitSkipPagination
    renderer_classes = [CustomJSONRenderer, BrowsableAPIRenderer, JSONRenderer]
    
    def list(self, request):
        queryset = Concession.objects.filter(customer__user=request.user)

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
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LimitSkipPagination
    renderer_classes = [CustomJSONRenderer, BrowsableAPIRenderer, JSONRenderer]
    
    def list(self, request):
        queryset = Usage.objects.filter(customer__user=request.user)

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


# Register view
def register(request):
    if request.method == 'POST':
        user_form = RegisterForm(request.POST)
        # Validate form
        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user.password)
            user.save()

            zebras = Operator.objects.get(name='Zebras')
            customer = Customer.objects.create(user=user, operator=zebras)

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            success(request, f"Congratulations, {user.first_name}! You've registered successfully!")
            return redirect(reverse('website:purchases'))
        else:
            print(user_form.errors)
    else:
        user_form = RegisterForm()

    context = {
        'registration_form': user_form,
    }
    return render(request, 'website/register.html', context)


# Login view
def customer_login(request):
    # If the user is logged in, redirect to the purchases page
    if request.user.is_authenticated:
        return redirect(reverse('website:purchases'))

    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        # Validate form
        if form.is_valid():
            loginName = form.cleaned_data['username']
            loginPass = form.cleaned_data['password']

            user = authenticate(username = loginName, password = loginPass)
            login(request, user)

            return redirect(reverse('website:purchases'))

    return render(request, 'website/login.html', {"form": form})


# Logout - redirect to login page
def customer_logout(request):
    logout(request)
    return redirect(reverse('website:login'))


# Connect view - allows logged in users to link accounts with other operators
def connect(request):
    # If the user is not logged in, redirect to the login page
    if not request.user.is_authenticated:
        return redirect(reverse('website:login'))
        
    if request.method == 'POST':
        if request.POST.get("username") and request.POST.get("password") and request.POST.get("id"):
            username = request.POST.get("username")
            password = request.POST.get("password")
            operator_id = request.POST.get("id")
            if operator_id == "292":
                cust = Customer.objects.get(user=request.user)
                connectedAccount = ConnectedAccount.objects.create(customer=cust, operator_id=operator_id, 
                        auth_url="N/A", access_token="N/A",
                        refresh_token="N/A")
            # Obtain a token for linking
            url = "https://cs20team.pythonanywhere.com/o/token/"
            r = requests.post("https://cs20team.pythonanywhere.com/o/token/", auth=HTTPBasicAuth(client_id, client_secret),
                data={"username" : username, "password" : password, "grant_type" : "password"})

            if r.status_code == 200:
                user = request.user
                data = json.loads(r.text)
                cust = Customer.objects.get(user=user)
                connectedAccount = ConnectedAccount.objects.create(customer=cust, operator_id=operator_id, 
                        auth_url="https://cs20team.pythonanywhere.com/o/token/", access_token=data["access_token"],
                        refresh_token=data["refresh_token"])

    operators = getOperators()

    # Paginate operators
    paginator = Paginator(operators, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get accounts that are already linked
    connectedAccs = ConnectedAccount.objects.filter(customer=Customer.objects.get(user=request.user))
    connectedAccs = [x.operator_id for x in connectedAccs]

    context = {"operators": page_obj, "connected": connectedAccs, "current_op": Operator.objects.all()[0]}
    return render(request, 'website/connect.html', context)


# Disconnect - lets users unlink accounts to not see tickets from certain operators
def disconnect(request, pk):
    cust = Customer.objects.get(user=request.user)
    connected = ConnectedAccount.objects.get(customer=cust, operator_id=pk)

    if request.method == 'POST':
        connected.delete()
        return redirect('website:connect')

    return connect(request)


# Display the user's purchases
def purchases(request):
    # If the user is not logged in, redirect to the login page
    if not request.user.is_authenticated:
        return redirect(reverse('website:login'))
    
    context = {}
    ticket_type = "purchase"
    context["ticket_type"] = ticket_type
    
    startdate, enddate = getDates(request, ticket_type)
    context['startdate'] = startdate
    context['enddate'] = enddate
        
    mode = request.POST.get("mode")
    if mode and mode != "None":
        context.update({"mode":mode})
        
    # Pass the message to display depending on the selected filters
    context["heading"] = generateTicketHeading(ticket_type, mode, startdate=startdate, enddate=enddate)

    # Retrieve a list of Purchases filtered by the given fields in the context dictionary
    context["purchases"] = getPurchases(request.user, context)
    
    # Retreive all Modes from the user's unfiltered Purchases
    context["modes"] = getModes(getPurchases(request.user))
    return render(request, 'website/purchases.html', context)


# Display the user's concessions
def concessions(request):
    # If the user is not logged in, redirect to the login page
    if not request.user.is_authenticated:
        return redirect(reverse('website:login'))

    context = {}
    ticket_type = "concession"
    context["ticket_type"] = ticket_type

    status = request.POST.get("status", "valid")
    context["status"] = status
    
    mode = request.POST.get("mode")
    if mode and mode != "None":
        context["mode"] = mode

    # Pass the message to display depending on the selected filters
    context["heading"] = generateTicketHeading(ticket_type, mode, status=status)

    # Obtain either current or past concessions for user 
    concessions = getConcessions(request.user, context)
    context['concessions'] = concessions
    
    # Retreive all Modes from the user's unfiltered Concessions
    context["modes"] = getModes(getConcessions(request.user))

    return render(request, 'website/concessions.html', context)


# Display the user's usages
def usage(request):
    # If the user is not logged in, redirect to the login page
    if not request.user.is_authenticated:
        return redirect(reverse('website:login'))

    context = {}
    ticket_type = "usage"
    context["ticket_type"] = ticket_type
    
    startdate, enddate = getDates(request, ticket_type)
    context['startdate'] = startdate
    context['enddate'] = enddate
    
    mode = request.POST.get("mode")
    if mode and mode != "None":
        context.update({"mode":mode})
        
    # Pass the message to display depending on the selected filters
    context["heading"] = generateTicketHeading(ticket_type, mode, startdate=startdate, enddate=enddate)

    # Obtain a list of usages for the user, possibly filtered
    usages = getUsage(request.user, context)
    context['usages'] = usages
    
    # Retreive all Modes from the user's unfiltered Usages
    context["modes"] = getModes(getUsage(request.user))
    return render(request, 'website/usage.html', context)
    