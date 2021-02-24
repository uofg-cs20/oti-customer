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


# Returns date filters
def getDates(request):
    startdate = request.POST.get("startdate")
    enddate = request.POST.get("enddate")

    # None given
    if not startdate and not enddate:
        return None

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
        enddate = None

    # Only enddate given
    if not startdate and enddate:
        startdate = None
        enddate = formatDate(enddate)

    return {"startdate":startdate, "enddate":enddate}


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
    local_purchases = Purchase.objects.filter(customer_id=customer.id)

    # Here we get the Purchases from linked Operator accounts
    if not filters.get("link") == False:
        linked_purchases = getPCU(user, 'purchase/?format=json')
        local_purchases = list(local_purchases)
        if linked_purchases:
            for purchase in linked_purchases:
                local_purchases.append(purchase)
                
    # Get the filters
    mode = filters.get("mode")
    startdate = filters.get("startdate", datetime.datetime.min.replace(tzinfo=pytz.UTC))
    enddate = filters.get("enddate", datetime.datetime.max.replace(tzinfo=pytz.UTC))

    # Filter by mode
    if mode:
        local_purchases = [p for p in local_purchases if p.mode == mode]

    # Filter by date, including all purchases whose "from-to" validity date range overlaps the filtered date range
    # First include those whose "from" date is within the filter range
    # Then include those whose "to" date is within the filter range
    # Finally include the special cases whose filter range is entirely within the "from-to" validity range
    local_purchases = [p for p in local_purchases if \
                        (p.travel_to_date_time >= startdate and p.travel_to_date_time <= enddate) \
                        or (p.travel_from_date_time >= startdate and p.travel_from_date_time <= enddate) \
                        or (p.travel_from_date_time <= startdate and p.travel_to_date_time >= enddate)]

    # Return all the user's Purchases sorted by travel_to_date_time
    return sorted(local_purchases, key=lambda x: x.travel_to_date_time)


def getConcessions(user, context):
    customer = Customer.objects.get(user=user)
    today = timezone.now()

    # Get the filters
    expired = context.get('expired')
    mode = context.get('mode')

    linked_conc = getPCU(user, 'concession/?format=json')

    if not expired and mode:
        # return valid concessions, filtered by mode
        # i.e. concessions with expiry date in the future
        if linked_conc:
            curmode = Mode.objects.get(short_desc=mode)
            concs = list(Concession.objects.filter(customer_id=customer.id, valid_to_date_time__gt=today, mode=curmode))
            for conc in linked_conc:
                if (conc.valid_to_date_time > today) and (conc.mode == curmode):
                    concs.append(conc)
            return sorted(concs, key=lambda x: x.valid_from_date_time)
        return Concession.objects.filter(customer_id=customer.id, valid_to_date_time__gt=today,
                                         mode=Mode.objects.get(short_desc=mode))

    elif expired and mode:
        # return expired concessions, filtered by mode
        # i.e. concessions with expiry date in the past
        if linked_conc:
            curmode = Mode.objects.get(short_desc=mode)
            concs = list(Concession.objects.filter(customer_id=customer.id, valid_to_date_time__lt=today, mode=curmode))
            for conc in linked_conc:
                if (conc.valid_to_date_time < today) and (conc.mode == curmode):
                    concs.append(conc)
            return sorted(concs, key=lambda x: x.valid_from_date_time)
        return Concession.objects.filter(customer_id=customer.id, valid_to_date_time__lt=today,
                                         mode=Mode.objects.get(short_desc=mode))

    elif not expired and not mode:
        # return all valid concessions
        if linked_conc:
            concs = list(Concession.objects.filter(customer_id=customer.id, valid_to_date_time__gt=today))
            for conc in linked_conc:
                if conc.valid_to_date_time > today:
                    concs.append(conc)
            return sorted(concs, key=lambda x: x.valid_from_date_time)
        return Concession.objects.filter(customer_id=customer.id, valid_to_date_time__gt=today)

    else:
        # return all expired concessions
        if linked_conc:
            concs = list(Concession.objects.filter(customer_id=customer.id, valid_to_date_time__lt=today))
            for conc in linked_conc:
                if conc.valid_to_date_time < today:
                    concs.append(conc)
            return sorted(concs, key=lambda x: x.valid_from_date_time)
        return Concession.objects.filter(customer_id=customer.id, valid_to_date_time__lt=today)


def getUsage(user, filters=None):
    cust = Customer.objects.get(user=user)

    # Get the filters
    mode = filters.get("mode")
    startdate = filters.get("startdate", datetime.datetime.min.replace(tzinfo=pytz.UTC))
    enddate = filters.get("enddate", datetime.datetime.max.replace(tzinfo=pytz.UTC))
    # Filter with the mode if given
    if (mode != 'None') and (mode is not None):
        usages = Usage.objects.filter(customer=cust.id, mode=Mode.objects.get(short_desc=mode))
    else:
        usages = Usage.objects.filter(customer=cust.id)

    # Filter usages by date & time
    usages = usages.filter(travel_to__date_time__range=[str(startdate), str(enddate)]) \
        .union(usages.filter(travel_from__date_time__range=[str(startdate), str(enddate)])) \
        .union(usages.filter(travel_from__date_time__lte=startdate, travel_to__date_time__gte=enddate))

    # Here we get the linked usages from other operators
    linked_usages = getPCU(user, 'usage/?format=json')
    usages = list(usages)
    if linked_usages:
        for usage in linked_usages:
            if (usage.travel_from.date_time < enddate) and (usage.travel_to.date_time >= startdate):
                usages.append(usage)
        return sorted(usages, key=lambda x: x.travel_from.date_time)
    else:
        return usages


# Returns a list of operators that can be linked
def getOperators():
    try:
        r = requests.get('https://cs20operator.herokuapp.com/api/operator/')
        catalogue = r.json()[0]["items"]
        out_list = ast.literal_eval(repr(catalogue).replace('-', '_'))
        return out_list
    except ConnectionError:
        return {"operators": {"null": "null"}}


# PCU stands for purchase, concession usage
# This function takes a user and the pcu and then proceeds to find the connected accounts tickets
# The function connects to an exposed API through authentication methods, and then creates Django models based on the
# data it interprets from the API. These models aren't saved in the database and are called every time a user connects
# to a page.
def getPCU(user, pcu):
    try:
        cust = Customer.objects.get(user=user)
        linked_accounts = ConnectedAccount.objects.filter(customer=cust)
        objs = []
        # Loop through all the linked accounts
        for linked_account in linked_accounts:
            r = requestData(linked_account, pcu)
            if not r:
                continue
            catalogue = r.json()
            out_list = ast.literal_eval(repr(catalogue).replace('-', '_'))
            # Loop through every ticket in the santizied list
            for ticket in out_list:
                # This section is for parts of each PCU that they all share
                # These are abstracted from the specific PCU to avoid repetition
                modeid = ticket['mode']['id']
                short_desc = ticket['mode']['short_desc']
                mode = Mode(id=modeid, short_desc=short_desc)

                optick = ticket['operator']
                opname = optick['name']
                homepage = optick['homepage']
                api_url = optick['api_url']
                phone = optick['phone']
                email = optick['email']
                operator = Operator(name=opname, homepage=homepage, api_url=api_url, phone=phone, email=email)

                recordid = RecordID(id=ticket['id'])
                latlongfrom, loc_from, latlongto, loc_to = getLocs(pcu.split('/')[0], ticket)

                if (pcu == "concession/?format=json") or (pcu == "purchase/?format=json"):
                    # These models are specific to concession and purchases
                    amount = ticket['transaction']['price']['amount']
                    currency = ticket['transaction']['price']['currency']
                    price = MonetaryValue(amount=amount, currency=currency)

                    date_time = formatdt(ticket['transaction']['date_time'])
                    reference = ticket['transaction']['reference']
                    payment_type = ticket['transaction']['payment_type']
                    payment_method = ticket['transaction']['payment_method']
                    trans = Transaction(date_time=date_time, reference=reference, payment_type=payment_type,
                                        payment_method=payment_method, price=price)

                if (pcu == "purchase/?format=json") or (pcu == "usage/?format=json"):
                    # These models are specific to purchases and usages
                    tc = TravelClass(travel_class=ticket['travel_class'])
                    reference = ticket['ticket']['reference']
                    number_usages = ticket['ticket']['number_usages']
                    reference_type = ticket['ticket']['reference_type']
                    medium = ticket['ticket']['medium']
                    tick = Ticket(reference=reference, number_usages=number_usages, reference_type=reference_type,
                                  medium=medium)

                # These next if statements are for creating the actual PCU models
                # They are appended to a list of objects when they are created
                if pcu == "concession/?format=json":
                    # These models are specific to concessions
                    discount_type = ticket['discount']['discount_type']
                    discount_value = ticket['discount']['discount_value']
                    discount_description = ticket['discount']['discount_description']
                    valid_from_date_time = formatdt(ticket['valid_from_date_time'])
                    valid_to_date_time = formatdt(ticket['valid_to_date_time'])
                    conditions = ticket['conditions']
                    disc = Discount(discount_type=discount_type, discount_value=discount_value,
                                    discount_description=discount_description)
                    concession = Concession(id=recordid, mode=mode, operator=operator, name=mode.short_desc,
                                            price=price, conditions=conditions, customer=cust, discount=disc,
                                            transaction=trans, valid_from_date_time=valid_from_date_time,
                                            valid_to_date_time=valid_to_date_time)
                    objs.append(concession)

                if pcu == "purchase/?format=json":
                    # These models are specific to purchases
                    amount = ticket['account_balance']['amount']
                    currency = ticket['account_balance']['currency']
                    balance = MonetaryValue(amount=amount, currency=currency)

                    reference = ticket['vehicle']['reference']
                    vehicle_type = ticket['vehicle']['vehicle_type']
                    vehicle = Vehicle(reference=reference, vehicle_type=vehicle_type)

                    booking_date_time = formatdt(ticket['booking_date_time'])
                    travel_from_date_time = formatdt(ticket['travel_from_date_time'])
                    travel_to_date_time = formatdt(ticket['travel_to_date_time'])
                    purchase = Purchase(id=recordid, mode=mode, operator=operator, travel_class=tc,
                                        booking_date_time=booking_date_time, transaction=trans, account_balance=balance,
                                        vehicle=vehicle, travel_from_date_time=travel_from_date_time,
                                        travel_to_date_time=travel_to_date_time, ticket=tick,
                                        location_from=loc_from, location_to=loc_to, customer=cust)
                    objs.append(purchase)

                if pcu == "usage/?format=json":
                    # These models are specific to usages
                    amount = ticket['price']['amount']
                    currency = ticket['price']['currency']
                    price = MonetaryValue(amount=amount, currency=currency)

                    date_time = formatdt(ticket['travel_from']['date_time'], False)
                    reference = ticket['travel_from']['reference']
                    uft1 = UsageFromTo(location=loc_from, date_time=date_time, reference=reference)

                    date_time = formatdt(ticket['travel_to']['date_time'], False)
                    reference = ticket['travel_from']['reference']
                    uft2 = UsageFromTo(location=loc_to, date_time=date_time, reference=reference)

                    reference = ticket['reference']['reference']
                    reference_type = ticket['reference']['reference_type']
                    ur = UsageReference(reference=reference, reference_type=reference_type)
                    usage = Usage(id=recordid, mode=mode, operator=operator, reference=ur, travel_class=tc,
                                  travel_from=uft1, travel_to=uft2, ticket=tick, price=price, customer=cust)
                    objs.append(usage)
        return objs
    except ConnectionError:
        return []
    except TypeError:
        return []


# This function is for creating the location data for each PCU. It has been abstracted because each object uses this
# function and keeping it in the getPCU() function created bloat. It runs through the ticket dictionary it is passed
# and created LatitudeLongitude and Location models. It also uses reverse geolocation to find the location of the ticket.
def getLocs(pcu, ticket):
    if pcu == 'concession':
        return [None, None, None, None]
    if pcu == 'usage':
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
def requestData(linked_account, pcu):
    try:
        token = linked_account.access_token
        refresh_token = linked_account.refresh_token
        r = requests.get('https://cs20operator.herokuapp.com/api/operator/')
        catalogue = r.json()[0]["items"]
        out_list = ast.literal_eval(repr(catalogue).replace('-', '_'))

        for op in out_list:
            if op["item_metadata"][3]["val"] == linked_account.operator_id:
                api_url = op["href"]

        r = requests.get(api_url + pcu, headers={"Authorization": "Bearer " + token})

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
                r = requests.get(api_url + pcu, headers={"Authorization": "Bearer " + linked_account.access_token})
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
        
