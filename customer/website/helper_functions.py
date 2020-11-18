from .models import Purchase
from datetime import datetime, timedelta
from django.utils import timezone
import pytz


# Returns a datetime object corresponding to the given date string of format "dd-mm-yyyy"
def formatDate(datestr):
    year = int(datestr[-4:])
    month = int(datestr[3:5])
    day = int(datestr[:2])
    return datetime(year, month, day)


# Returns the Purchases of the given user, filtered by the given dates
def getPurchases(user, startdate=timezone.now()-timedelta(days=30), enddate=timezone.now()):
    return Purchase.objects.filter(customer_id=user.id, booking_date_time__range=[str(startdate),str(enddate)])
