import sys
sys.path.append("..")

from .models import *
from datetime import timedelta
import datetime
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
import pytz
import requests
from requests.exceptions import ConnectionError
import ast
from requests.auth import HTTPBasicAuth
import json
import extra.reverse_geocode as reverse_geocode

client_id = "ou9h2JlNWlch0Vj7N2AzK6qYANdNIl1Mo7gg1oZj"
client_secret = "5EUIoebBH2SxgjANJ6KL1q1GcGZn924OCQbhbysqQ9kb79W3i9YBDGbMGlYw1NPee40fI3t0OYFW2zaghGl5buKfUzGQc7XuibqpbA296LKNiWWuF02RUUBaDAydV7t9"


# Returns the available modes of transport
def getModes():
    local_modes = Mode.objects.all()

    ### Here we would also get the Modes offered by linked Operators ###
    linked_modes = Mode.objects.none()

    # Return all modes of transport offered by this Operator and linked Operators
    modes = local_modes.union(linked_modes)
    return modes


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


# Returns the Purchases of the given user, filtered by the given dates and mode of transport
def getPurchases(user, filters):
    # Get the Customer object of the given user
    customer = Customer.objects.get(user=user)

    # Filter by user
    local_purchases = list(Purchase.objects.filter(customer_id=customer.id))

    # Here we get the Purchases from linked Operator accounts
    if not filters.get("link") == False:
        linked_purchases = getendpoints(user, 'purchase/?format=json')
        if linked_purchases:
            for purchase in linked_purchases:
                local_purchases.append(purchase)
                
    # Get the filters
    mode = filters.get("mode")
    startdate = filters.get("startdate", datetime.datetime.min.replace(tzinfo=pytz.UTC))
    enddate = filters.get("enddate", datetime.datetime.max.replace(tzinfo=pytz.UTC))

    # Filter by mode
    if mode and mode != "None":
        local_purchases = [p for p in local_purchases if p.mode.short_desc == mode]

    # Filter by date, including all purchases whose "from-to" validity date range overlaps the filtered date range
    # First include those whose "from" date is within the filter range
    # Then include those whose "to" date is within the filter range
    # Finally include the special cases whose filter range is entirely within the "from-to" validity range
    local_purchases = [p for p in local_purchases if \
                        (p.travel_to_date_time >= startdate and p.travel_to_date_time <= enddate) \
                        or (p.travel_from_date_time >= startdate and p.travel_from_date_time <= enddate) \
                        or (p.travel_from_date_time <= startdate and p.travel_to_date_time >= enddate)]

    # Return the user's Purchases sorted by travel_to_date_time
    return sorted(local_purchases, key=lambda x: x.travel_to_date_time)


# Returns the Concessions of the given user, filtered by the given status and mode of transport
def getConcessions(user, context):
    customer = Customer.objects.get(user=user)
    today = timezone.now()
    
    # Filter by user
    local_concessions = list(Concession.objects.filter(customer_id=customer.id))

    # Here we get the Concessions from linked Operator accounts
    if not context.get("link") == False:
        linked_concessions = getendpoints(user, 'concession/?format=json')
        if linked_concessions:
            for c in linked_concessions:
                local_concessions.append(c)
                
    # Get the filters
    status = context.get('status')
    mode = context.get('mode')
    
    # Filter by mode
    if mode and mode != "None":
        local_concessions = [c for c in local_concessions if c.mode.short_desc == mode]
        
    # Filter by status (valid or expired)
    if status == "past":
        local_concessions = [c for c in local_concessions if c.valid_to_date_time < today]
    else:
        local_concessions = [c for c in local_concessions if c.valid_to_date_time > today]
        
    # Return the user's Concessions sorted by valid_from_date_time
    return sorted(local_concessions, key=lambda x: x.valid_from_date_time)


# Returns the Usages of the given user, filtered by the given dates and mode of transport
def getUsage(user, filters=None):
    # Get the Customer object of the given user
    customer = Customer.objects.get(user=user)

    # Filter by user
    local_usages = list(Usage.objects.filter(customer_id=customer.id))

    # Here we get the Usages from linked Operator accounts
    if not filters.get("link") == False:
        linked_usages = getendpoints(user, 'usage/?format=json')
        if linked_usages:
            for usage in linked_usages:
                local_usages.append(usage)
                
    # Get the filters
    mode = filters.get("mode")
    startdate = filters.get("startdate", datetime.datetime.min.replace(tzinfo=pytz.UTC))
    enddate = filters.get("enddate", datetime.datetime.max.replace(tzinfo=pytz.UTC))

    # Filter by mode
    if mode and mode != "None":
        local_usages = [u for u in local_usages if u.mode.short_desc == mode]

    # Filter by date, including all usages whose "from-to" validity date range overlaps the filtered date range
    # First include those whose "from" date is within the filter range
    # Then include those whose "to" date is within the filter range
    # Finally include the special cases whose filter range is entirely within the "from-to" validity range
    local_usages = [u for u in local_usages if \
                        (u.travel_to.date_time >= startdate and u.travel_to.date_time <= enddate) \
                        or (u.travel_from.date_time >= startdate and u.travel_from.date_time <= enddate) \
                        or (u.travel_from.date_time <= startdate and u.travel_to.date_time >= enddate)]

    # Return the user's Usages sorted by travel_from.date_time
    return sorted(local_usages, key=lambda x: x.travel_from.date_time)
    

# Returns a list of operators that can be linked
def getOperators():
    try:
        r = requests.get('https://cs20operator.herokuapp.com/api/operator/')
        catalogue = r.json()[0]["items"]
        out_list = ast.literal_eval(repr(catalogue).replace('-', '_'))
        return out_list
    except ConnectionError:
        return {"operators": {"null": "null"}}


# This function takes a user and the endpoint and then proceeds to find the connected accounts tickets
# The function connects to an exposed API through authentication methods, and then creates Django models based on the
# data it interprets from the API. These models aren't saved in the database and are called every time a user connects
# to a page.
def getendpoints(user, endpoint):
    try:
        cust = Customer.objects.get(user=user)
        linked_accounts = ConnectedAccount.objects.filter(customer=cust)
        objs = []

        # Loop through all the linked accounts
        for linked_account in linked_accounts:
            r = requestData(linked_account, endpoint)
            if not r:
                continue
            catalogue = r.json()
            out_list = ast.literal_eval(repr(catalogue).replace('-', '_'))

            # Loop through every ticket in the santizied list
            for ticket in out_list:
                # This section is for parts of each endpoint that they all share
                # These are abstracted from the specific endpoint to avoid repetition
                mode = getMode(ticket['mode'])
                operator = getOperator(ticket['operator'])
                recordid = RecordID(id=ticket['id'])

                api_endpoint = getApi(endpoint)

                latlongfrom, loc_from, latlongto, loc_to = getLocs(api_endpoint, ticket)

                if (api_endpoint == "concession"):
                    concession = getTicketConcession(ticket)
                    objs.append(concession)

                elif (api_endpoint == "purchase"):
                    purchase = getTicketPurchase(ticket, loc_from, loc_to)
                    objs.append(purchase)

                elif (api_endpoint == "usage"):    
                    usage = getTicketUsage(ticket, loc_from, loc_to)
                    objs.append(usage)

        return objs
    except ConnectionError:
        return []
    except TypeError:
        return []


# This function is for creating the location data for each endpoint. It has been abstracted because each object uses this
# function and keeping it in the getendpoints() function created bloat. It runs through the ticket dictionary it is passed
# and created LatitudeLongitude and Location models. It also uses reverse geolocation to find the location of the ticket.
def getLocs(endpoint, ticket):
    if endpoint == 'concession':
        return [None, None, None, None]
    if endpoint == 'usage':
        ticketfrom = ticket['travel_from']['location']
        ticketto = ticket['travel_to']['location']
    else:
        ticketfrom = ticket['location_from']
        ticketto = ticket['location_to']
    ticketfrom = ast.literal_eval(repr(ticketfrom).replace('_', '-'))
    ticketto = ast.literal_eval(repr(ticketto).replace('_', '-'))

    latfrom = ticketfrom['lat-long']['latitude']
    longfrom = ticketfrom['lat-long']['longitude']
    latlongfrom = LatitudeLongitude(latitude=latfrom, longitude=longfrom)
    name = reverse_geocode.search([(float(latfrom), float(longfrom))])[0]['city']
    loc_from = Location(lat_long=latlongfrom, NaPTAN=ticketfrom['NaPTAN'], name=name)

    latto = ticketto['lat-long']['latitude']
    longto = ticketto['lat-long']['longitude']
    latlongto = LatitudeLongitude(latitude=latto, longitude=longto)
    name = reverse_geocode.search([(float(latto), float(longto))])[0]['city']
    loc_to = Location(lat_long=latlongto, NaPTAN=ticketto['NaPTAN'], name=name)
    return [latlongfrom, loc_from, latlongto, loc_to]


# formatdt is used for making sure each datetime that is read in, is in the correct format and so can be turned into
# a datetime object.
def formatdt(time, nano=True):
    time = time.replace('_', '-')
    if nano and (len(time) > 20):
        time = datetime.datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=pytz.UTC)
        return time.replace(microsecond=0)
    else:
        return datetime.datetime.strptime(time, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.UTC)


# Requests access to a linked operator site using a token
def requestData(linked_account, endpoint):
    try:
        token = linked_account.access_token
        refresh_token = linked_account.refresh_token
        r = requests.get('https://cs20operator.herokuapp.com/api/operator/')
        catalogue = r.json()[0]["items"]
        out_list = ast.literal_eval(repr(catalogue).replace('-', '_'))

        for op in out_list:
            if op["item_metadata"][3]["val"] == linked_account.operator_id:
                api_url = op["href"]

        r = requests.get(api_url + endpoint, headers={"Authorization": "Bearer " + token})

        if r.status_code != 200:
            # possible refresh
            r = requests.post("https://cs20team.pythonanywhere.com/o/token/",
                              auth=HTTPBasicAuth(client_id, client_secret),
                              data={"grant_type": "refresh_token", "refresh_token": refresh_token})
            if r.status_code == 200:
                # refresh worked
                data = json.loads(r.text)
                linked_account.access_token = data["access_token"]
                linked_account.refresh_token = data["refresh_token"]
                linked_account.save()
                r = requests.get(api_url + endpoint, headers={"Authorization": "Bearer " + linked_account.access_token})
            else:
                return None

        return r

    except:
        pass
        
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
        

def getTicketPurchase(ticket):
    price = getMonetaryValue(ticket['transaction']['price'])
    trans = getTransaction(ticket['transaction'], price)
    tc = TravelClass(travel_class=ticket['travel_class'])
    tick = getTicket(ticket['ticket'])
    balance = getMonetaryValue(ticket['account_balance'])
    vehicle = getVehicle(ticket['vehicle'])

    booking_date_time = formatdt(ticket['booking_date_time'])
    travel_from_date_time = formatdt(ticket['travel_from_date_time'])
    travel_to_date_time = formatdt(ticket['travel_to_date_time'])
    return Purchase(id=recordid, mode=mode, operator=operator, travel_class=tc,
                        booking_date_time=booking_date_time, transaction=trans, account_balance=balance,
                        vehicle=vehicle, travel_from_date_time=travel_from_date_time,
                        travel_to_date_time=travel_to_date_time, ticket=tick,
                        location_from=loc_from, location_to=loc_to, customer=cust)


def getTicketConcession(ticket):
    price = getMonetaryValue(ticket['transaction']['price'])
    trans = getTransaction(ticket['transaction'], price)
    disc = getDiscount(ticket['discount'])
    valid_from_date_time = formatdt(ticket['valid_from_date_time'])
    valid_to_date_time = formatdt(ticket['valid_to_date_time'])
    conditions = ticket['conditions']
    concession = Concession(id=recordid, mode=mode, operator=operator, name=mode.short_desc,
                            price=price, conditions=conditions, customer=cust, discount=disc,
                            transaction=trans, valid_from_date_time=valid_from_date_time,
                            valid_to_date_time=valid_to_date_time)


def getTicketUsage(ticket):
    tc = TravelClass(travel_class=ticket['travel_class'])
    tick = getTicket(ticket['ticket'])
    price = getMonetaryValue(ticket['price'])

    date_time = formatdt(ticket['travel_from']['date_time'], False)
    reference = ticket['travel_from']['reference']
    uft1 = UsageFromTo(location=loc_from, date_time=date_time, reference=reference)

    date_time = formatdt(ticket['travel_to']['date_time'], False)
    reference = ticket['travel_from']['reference']
    uft2 = UsageFromTo(location=loc_to, date_time=date_time, reference=reference)

    ur = getReference(ticket['reference'])

    return Usage(id=recordid, mode=mode, operator=operator, reference=ur, travel_class=tc,
                    travel_from=uft1, travel_to=uft2, ticket=tick, price=price, customer=cust)


def getMode(ticket):
    modeid = ticket['id']
    short_desc = ticket['short_desc']
    return Mode(id=modeid, short_desc=short_desc)


def getOperator(ticket):
    opname = ticket['name']
    homepage = ticket['homepage']
    api_url = ticket['api_url']
    phone = ticket['phone']
    email = ticket['email']
    return Operator(name=opname, homepage=homepage, api_url=api_url, phone=phone, email=email)


def getMonetaryValue(ticket):
    amount = ticket['amount']
    currency = ticket['currency']
    return MonetaryValue(amount=amount, currency=currency)


def getTransaction(ticket, price):
    date_time = formatdt(ticket['date_time'])
    reference = ticket['reference']
    payment_type = ticket['payment_type']
    payment_method = ticket['payment_method']
    return Transaction(date_time=date_time, reference=reference, payment_type=payment_type,
                        payment_method=payment_method, price=price)


def getTicket(ticket):
    reference = ticket['reference']
    number_usages = ticket['number_usages']
    reference_type = ticket['reference_type']
    medium = ticket['medium']
    tick = Ticket(reference=reference, number_usages=number_usages, reference_type=reference_type,
                    medium=medium)


def getDiscount(ticket):
    discount_type = ticket['discount_type']
    discount_value = ticket['discount_value']
    discount_description = ticket['discount_description']
    disc = Discount(discount_type=discount_type, discount_value=discount_value,
                    discount_description=discount_description)


def getVehicle(ticket):
    reference = ticket['reference']
    vehicle_type = ticket['vehicle_type']
    return Vehicle(reference=reference, vehicle_type=vehicle_type)


def getReference(ticket):
    reference = ticket['reference']['reference']
    reference_type = ticket['reference']['reference_type']
    return UsageReference(reference=reference, reference_type=reference_type)

def getApi(endpoint):
    endpoints = ['purchase', 'concession', 'usage']

    for i in endpoint.split('/'):
        if i in endpoints:
            return i
    