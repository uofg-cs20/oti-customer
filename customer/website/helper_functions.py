from .models import Mode, Purchase, Usage, Customer, Operator, Concession, Location
from datetime import timedelta
import datetime
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
import pytz
import requests
from requests.exceptions import ConnectionError
import ast


# Returns the available modes of transport
def getModes():
    local_modes = Mode.objects.all()

    ### Here we would also get the Modes offered by linked Operators ###
    linked_modes = Mode.objects.none()

    # Return all modes of transport offered by this Operator and linked Operators
    modes = local_modes.union(linked_modes)
    return modes


# Returns date filters
def getDates(request):
    startdate = request.POST.get("startdate")
    enddate = request.POST.get("enddate")

    # Both given
    if startdate and enddate:
        startdate = formatDate(startdate)
        enddate = formatDate(enddate)
    
    # Swap if start date > enddate
    if startdate and enddate  and startdate > enddate:
        startdate, enddate = enddate, startdate

    # Only startdate given
    if startdate and not enddate:
        startdate = formatDate(startdate)
        enddate = datetime.datetime.max.replace(tzinfo=pytz.UTC)
    
    # Only enddate given
    if not startdate and enddate:
        startdate = datetime.datetime.min.replace(tzinfo=pytz.UTC)
        enddate = formatDate(enddate)

    # None given
    if not startdate and not enddate:
        startdate = timezone.now()
        enddate = timezone.now() + timedelta(days=30)

    return (startdate, enddate)


# Returns a datetime object corresponding to the given date string of format "dd-mm-yyyy"
def formatDate(datestr):
    year = int(datestr[-4:])
    month = int(datestr[3:5])
    day = int(datestr[:2])
    # For timezone-awareness call .replace(tzinfo=pytz.UTC) on the created datetime object
    return datetime.datetime(year, month, day).replace(tzinfo=pytz.UTC)


# Returns the Purchases of the given user, filtered by the given dates and mode of transport
def getPurchases(user, filters):
    # Get the Customer object of the given user
    customer = Customer.objects.get(user=user)
    
    # Get the filters
    mode = filters.get("mode")
    startdate = filters.get("startdate", datetime.datetime.min.replace(tzinfo=pytz.UTC))
    enddate = filters.get("enddate", datetime.datetime.max.replace(tzinfo=pytz.UTC))

    # Filter by the user and mode
    if mode:
        local_purchases = Purchase.objects.filter(customer_id=customer.id, mode=Mode.objects.get(short_desc=mode))
    else:
        local_purchases = Purchase.objects.filter(customer_id=customer.id)

    # Filter by date, including all purchases whose "from-to" validity date range overlaps the filtered date range
    # First include those whose "from" date is within the filter range
    # Then include those whose "to" date is within the filter range
    # Finally include the special cases whose filter range is entirely within the "from-to" validity range
    local_purchases = local_purchases.filter(travel_to_date_time__range=[str(startdate), str(enddate)]) \
        .union(local_purchases.filter(travel_from_date_time__range=[str(startdate), str(enddate)])) \
        .union(local_purchases.filter(travel_from_date_time__lte=startdate, travel_to_date_time__gte=enddate))

    ### Here we would also get the Purchases from linked Operator accounts ###
    linked_purchases = Purchase.objects.none()
    if filters.get("link"):
        pass

    # Return all the user's Purchases sorted by travel_to_date_time
    purchases = local_purchases.union(linked_purchases)
    return purchases.order_by("travel_to_date_time")


def getConcessions(user, context):
    customer = Customer.objects.get(user=user)
    today = timezone.now()

    # Get the filters
    expired = context.get('expired')
    mode = context.get('mode')

    if not expired and mode:
        # return valid concessions
        # i.e. concessions with expiry date in the future
        return Concession.objects.filter(customer_id=customer.id, valid_to_date_time__gt=today, mode=Mode.objects.get(short_desc=mode))

    elif expired and mode:
        # return expired concessions
        # i.e. concessions with expiry date in the past
        return Concession.objects.filter(customer_id=customer.id, valid_to_date_time__lt=today, mode=Mode.objects.get(short_desc=mode))

    elif not expired and not mode:
        return Concession.objects.filter(customer_id=customer.id, valid_to_date_time__gt=today)

    else:
        return Concession.objects.filter(customer_id=customer.id, valid_to_date_time__lt=today)


def getUsage(user, filters=None):
    cust = Customer.objects.get(user=user)

    # Get the filters
    mode = filters.get("mode")
    startdate = filters.get("startdate")
    enddate = filters.get("enddate")
    # Filter with the mode if given
    if mode != 'None':
        usages = Usage.objects.filter(customer=cust.id, mode=Mode.objects.get(short_desc=mode))
    else:
        usages = Usage.objects.filter(customer=cust.id)

    usages = usages.filter(travel_to__date_time__range=[str(startdate), str(enddate)]) \
        .union(usages.filter(travel_from__date_time__range=[str(startdate), str(enddate)])) \
        .union(usages.filter(travel_from__date_time__lte=startdate, travel_to__date_time__gte=enddate))
        
    return usages


def getOperators():
    try:
        r = requests.get('http://127.0.0.1:8001/api/?operator=all')
        catalogue = r.json()["items"]
        out_list = ast.literal_eval(repr(catalogue).replace('-', '_'))
        return out_list
    except ConnectionError:
        return {"operators": {"null": "null"}}