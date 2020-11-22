from .models import Mode, Purchase, Usage, Customer, Account, Concession
from datetime import timedelta
import datetime
from django.utils import timezone
import pytz


# Returns the available modes of transport
def getModes():
    local_modes = Mode.objects.all()

    # Here we would also get the Modes offered by linked Operators

    return local_modes


# Returns a datetime object corresponding to the given date string of format "dd-mm-yyyy"
def formatDate(datestr):
    year = int(datestr[-4:])
    month = int(datestr[3:5])
    day = int(datestr[:2])
    # For timezone-awareness call .replace(tzinfo=pytz.UTC) on the created datetime object
    return datetime.datetime(year, month, day).replace(tzinfo=pytz.UTC)


# Returns the Purchases of the given user, filtered by the given dates and mode of transport
def getPurchases(user, filters):
    # If both the start date and end date aren't provided, filter the next 30 days
    if not (filters.get("startdate") or filters.get("enddate")):
        startdate = timezone.now()
        enddate = timezone.now()+timedelta(days=30)
    # Otherwise filter with the dates that have been given
    else:
        startdate = filters.get("startdate", datetime.datetime.min.replace(tzinfo=pytz.UTC))
        enddate = filters.get("enddate", datetime.datetime.max.replace(tzinfo=pytz.UTC))
        
    # Filter by the mode if given, and sort the Purchases by date
    local_purchases = []
    if filters.get("mode"):
        local_purchases = Purchase.objects.filter(customer_id=user.id, travel_from_date_time__range=[str(startdate),str(enddate)], mode=filters.get("mode")).order_by("travel_from_date_time")
    else:
        local_purchases = Purchase.objects.filter(customer_id=user.id, travel_from_date_time__range=[str(startdate),str(enddate)]).order_by("travel_from_date_time")

    # Here we would also get the Purchases from linked Operator accounts

    return local_purchases

def getConcessions(user, context):
    today = timezone.now()
    status = context["status"]

    if (status == "valid" or status == " ") and context.get("mode"):
        mode = context["mode"]
        # return valid concessions
        # i.e. concessions with expiry date in the future
        return Concession.objects.filter(customer_id=user.id, valid_to_date_time__gt=today, mode=mode)

    elif status == "past" and context.get("mode"):
        mode = context["mode"]
        # return expired concessions
        # i.e. concessions with expiry date in the past
        return Concession.objects.filter(customer_id=user.id, valid_to_date_time__lt=today, mode=mode)

    elif status == "valid" and not context.get("mode"):
        return Concession.objects.filter(customer_id=user.id, valid_to_date_time__gt=today)

    else:
        return Concession.objects.filter(customer_id=user.id, valid_to_date_time__lt=today)

def getUsage(user):
    tickets = []
    try:
        cust = Customer.objects.get(user=user)
        for usages in Usage.objects.filter(customer=cust.id):
            tickets.append([usages, Account.objects.filter(customer_id=cust.id)])
    except TypeError:
        pass
    return tickets