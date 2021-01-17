from .models import Mode, Purchase, Usage, Customer, Account, Concession, Location
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

    # If both the start date and end date aren't provided, filter the next 30 days
    if not (filters.get("startdate") or filters.get("enddate")):
        startdate = timezone.now()
        enddate = timezone.now() + timedelta(days=30)
    # Otherwise filter with the dates that have been given
    else:
        startdate = filters.get("startdate", datetime.datetime.min.replace(tzinfo=pytz.UTC))
        enddate = filters.get("enddate", datetime.datetime.max.replace(tzinfo=pytz.UTC))

    # Filter by the user and mode
    # This function assumes that the given startdate will be before the given enddate chronologically
    if filters.get("mode"):
        local_purchases = Purchase.objects.filter(customer_id=customer.id, mode=Mode.objects.get(short_desc=filters.get("mode")))
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
    today = timezone.now()
    status = context["status"]

    customer = Customer.objects.get(user=user)

    if status == "valid" and context.get("mode"):
        mode = context["mode"]
        # return valid concessions
        # i.e. concessions with expiry date in the future
        return Concession.objects.filter(customer_id=customer.id, valid_to_date_time__gt=today, mode=Mode.objects.get(short_desc=mode))

    elif not status and context.get("mode"):
        mode = context["mode"]
        # return expired concessions
        # i.e. concessions with expiry date in the past
        return Concession.objects.filter(customer_id=customer.id, valid_to_date_time__lt=today, mode=Mode.objects.get(short_desc=mode))

    elif status == "valid" and not context.get("mode"):
        return Concession.objects.filter(customer_id=customer.id, valid_to_date_time__gt=today)

    else:
        return Concession.objects.filter(customer_id=customer.id, valid_to_date_time__lt=today)


def getUsage(user, filters=None):
    tickets = {}
    startdate = filters[0]
    enddate = filters[1]
    mode = filters[2]
    try:
        if not startdate:
            startdate = timezone.now() - timedelta(days=30)
        if not enddate:
            enddate = timezone.now()
        if enddate < startdate:
            startdate, enddate = enddate, startdate
        cust = Customer.objects.get(user=user)

        if (mode) and (mode != "None"):
            usages = Usage.objects.filter(customer=cust.id, mode=mode)
        else:
            usages = Usage.objects.filter(customer=cust.id)
        usages = usages.filter(travel_to__date_time__range=[str(startdate), str(enddate)]) \
            .union(usages.filter(travel_from__date_time__range=[str(startdate), str(enddate)])) \
            .union(usages.filter(travel_from__date_time__lte=startdate, travel_to__date_time__gte=enddate))
        for usage in usages:
            usage_dict = {"usage": usage}
            operator = Account.objects.get(customer_id=cust.id)
            usage_dict["operator"] = operator.operator_id
            usage_dict["locs"] = [usage.travel_from.location.name, usage.travel_to.location.name]
            usage_dict["date"] = [usage.travel_from.date_time, usage.travel_to.date_time]
            usage_dict["mode"] = usage.mode
            tickets[usage.id] = usage_dict
    except ObjectDoesNotExist:
        pass
    return tickets


def getOperators():
    try:
        r = requests.get('http://127.0.0.1:8001/api/?operator=all')
        catalogue = r.json()["items"]
        out_list = ast.literal_eval(repr(catalogue).replace('-', '_'))
        print(out_list)
        return out_list
    except ConnectionError:
        return {"operators": {"null": "null"}}