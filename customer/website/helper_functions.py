import sys
sys.path.append("..")

from .models import *
from datetime import timedelta
import datetime
from django.utils import timezone
import pytz


# Returns date filters for the given ticket request
def getDates(request, ticket_type):
    startdate = request.POST.get("startdate")
    enddate = request.POST.get("enddate")

    # Both given
    if startdate and enddate:
        startdate = formatDate(startdate)
        enddate = formatDate(enddate)

    # Swap if start date > enddate
    if startdate and enddate and startdate > enddate:
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
        if ticket_type == "usage":
            startdate = timezone.now() - timedelta(days=30)
            enddate = timezone.now()
        else:
            startdate = timezone.now()
            enddate = timezone.now() + timedelta(days=30)

    return (startdate, enddate)
    

# Generates the message for displaying tickets when a filter is applied
# ticket_type is a string, e.g. "purchase"
# startdate & enddate are datetime objects
# mode is a string, e.g. "Train"
def generateTicketHeading(ticket_type, mode, startdate=None, enddate=None, status=None):
    message = "Displaying "
    
    # Concessions have a different message as they don't have a date filter
    if ticket_type == "concession":
        message = message + status + " "
        if mode and mode!= "None":
            message = message + mode.capitalize()
        message = message + " concessions"
        return message
        
    else:
        if mode and mode != "None":
            message = message + mode.capitalize() + " "
        else:
            message = message + "all "
        message = message + ticket_type + "s "
        
        # Handle the dates
        default_days = 30
        datetime_diff = enddate - startdate
        if datetime_diff > timedelta(days=default_days-1) and datetime_diff < timedelta(days=default_days+1):
            if startdate == timezone.now():
                message = message + "for the next " + str(default_days) + " days"
            elif enddate == timezone.now():
                message = message + "for the last " + str(default_days) + " days"
            else:
                message = message + "between " + str(startdate.date()) + " and " + str(enddate.date())
        elif startdate == datetime.datetime.min.replace(tzinfo=pytz.UTC):
            message = message + "before " + str(enddate.date())
        elif enddate == datetime.datetime.max.replace(tzinfo=pytz.UTC):
            message = message + "after " + str(startdate.date())
        else:
            message = message + "between " + str(startdate.date()) + " and " + str(enddate.date())
            
        return message


# Returns a datetime object corresponding to the given date string of format "dd-mm-yyyy"
def formatDate(datestr):
    year = int(datestr[-4:])
    month = int(datestr[3:5])
    day = int(datestr[:2])
    # For timezone-awareness call .replace(tzinfo=pytz.UTC) on the created datetime object
    return datetime.datetime(year, month, day).replace(tzinfo=pytz.UTC)


# formatdt is used for making sure each datetime that is read in, is in the correct format and so can be turned into
# a datetime object.
def formatdt(time, nano=True):
    time = time.replace('_', '-')
    if nano and (len(time) > 20):
        time = datetime.datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=pytz.UTC)
        return time.replace(microsecond=0)
    else:
        return datetime.datetime.strptime(time, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.UTC)

        
def emptyDatabase():
    # Delete data if the database is already populated
    if User.objects.all():
        User.objects.all().delete()
    if Customer.objects.all():
        Customer.objects.all().delete()
    if Operator.objects.all():
        Operator.objects.all().delete()
    if MonetaryValue.objects.all():
        MonetaryValue.objects.all().delete()
    if Discount.objects.all():
        Discount.objects.all().delete()
    if Concession.objects.all():
        Concession.objects.all().delete()
    if Purchase.objects.all():
        Purchase.objects.all().delete()
    if Location.objects.all():
        Location.objects.all().delete()
    if Vehicle.objects.all():
        Vehicle.objects.all().delete()
    if LatitudeLongitude.objects.all():
        LatitudeLongitude.objects.all().delete()
    if Usage.objects.all():
        Usage.objects.all().delete()
    if UsageReference.objects.all():
        UsageReference.objects.all().delete()
    if UsageFromTo.objects.all():
        UsageFromTo.objects.all().delete()
    if Service.objects.all():
        Service.objects.all().delete()
    if TravelClass.objects.all():
        TravelClass.objects.all().delete()
    if Ticket.objects.all():
        Ticket.objects.all().delete()
    if RecordID.objects.all():
        RecordID.objects.all().delete()
    if Mode.objects.all():
        Mode.objects.all().delete()
        
    