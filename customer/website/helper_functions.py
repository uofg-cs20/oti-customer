from .models import Mode, Purchase
from datetime import timedelta
import datetime
from django.utils import timezone
import pytz


# Returns a datetime object corresponding to the given date string of format "dd-mm-yyyy"
def formatDate(datestr):
    year = int(datestr[-4:])
    month = int(datestr[3:5])
    day = int(datestr[:2])
    # For timezone-awareness call .replace(tzinfo=pytz.UTC) on the created datetime object
    return datetime.datetime(year, month, day).replace(tzinfo=pytz.UTC)


# Returns the Purchases of the given user, filtered by the given dates and mode of transport
def getPurchases(user, filters):
    # If both the start date and end date aren't provided, filter the last 30 days
    if not (filters.get("startdate") or filters.get("enddate")):
        startdate = timezone.now()-timedelta(days=30)
        enddate = timezone.now()
    # Otherwise filter with the dates that have been given
    else:
        startdate = filters.get("startdate", datetime.datetime.min.replace(tzinfo=pytz.UTC))
        enddate = filters.get("enddate", datetime.datetime.max.replace(tzinfo=pytz.UTC))
        
    # Filter by the mode if given
    if filters.get("mode"):
        return Purchase.objects.filter(customer_id=user.id, booking_date_time__range=[str(startdate),str(enddate)], mode=filters.get("mode"))
    else:
        return Purchase.objects.filter(customer_id=user.id, booking_date_time__range=[str(startdate),str(enddate)])

