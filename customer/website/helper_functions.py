from .models import Mode, Purchase, Usage, Customer, Account, Concession
from datetime import timedelta
import datetime
from django.utils import timezone
import pytz


# Returns the available modes of transport
def getModes():
    local_modes = Mode.objects.all()

    ### Here we would also get the Modes offered by linked Operators ###
    linked_modes = Mode.objects.none()

    # Return all modes of transport offered by this Operator and linked Operators
    modes = local_modes.union(linked_modes)
    return modes


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
    
    # Filter by the user, mode and dates
    # This function assumes that the given startdate will be before the given enddate chronologically
    if filters.get("mode"):
        local_purchases = Purchase.objects.filter(customer_id=user.id, mode=filters.get("mode"))
    else:
        local_purchases = Purchase.objects.filter(customer_id=user.id)
    local_purchases = local_purchases.filter(travel_to_date_time__range=[str(startdate),str(enddate)]).union(local_purchases.filter(travel_from_date_time__range=[str(startdate),str(enddate)])).union(local_purchases.filter(travel_from_date_time__lte=startdate, travel_to_date_time__gte=enddate))
    
    ### Here we would also get the Purchases from linked Operator accounts ###
    linked_purchases = Purchase.objects.none()

    # Return all the user's Purchases sorted by travel_to_date_time
    purchases = local_purchases.union(linked_purchases)
    return purchases.order_by("travel_to_date_time")

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