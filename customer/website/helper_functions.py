from .models import *
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
        if request.POST.get("usages"):
            startdate = timezone.now() - timedelta(days=30)
            enddate = timezone.now()
        else:
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
    linked_purchases = getPCU('http://127.0.0.1:8000/api/', 'purchase/?format=json')
    local_purchases = list(local_purchases)
    if linked_purchases:
        for purchase in linked_purchases:
            local_purchases.append(purchase)

    # Return all the user's Purchases sorted by travel_to_date_time
    return sorted(local_purchases, key=lambda x: x.travel_from_date_time)


def getConcessions(user, context):
    customer = Customer.objects.get(user=user)
    today = timezone.now()

    # Get the filters
    expired = context.get('expired')
    mode = context.get('mode')

    linked_conc = getPCU('http://127.0.0.1:8000/api/', 'concession/?format=json')

    if not expired and mode:
        # return valid concessions
        # i.e. concessions with expiry date in the future
        curmode = Mode.objects.get(short_desc=mode)
        concs = list(Concession.objects.filter(customer_id=customer.id, valid_to_date_time__gt=today, mode=curmode))
        for conc in linked_conc:
            if (conc.valid_to_date_time > today) and (conc.mode == curmode):
                concs.append(conc)
        return sorted(concs, key=lambda x: x.valid_from_date_time)

    elif expired and mode:
        # return expired concessions
        # i.e. concessions with expiry date in the past
        curmode = Mode.objects.get(short_desc=mode)
        concs = list(Concession.objects.filter(customer_id=customer.id, valid_to_date_time__lt=today, mode=curmode))
        for conc in linked_conc:
            if (conc.valid_to_date_time < today) and (conc.mode == curmode):
                concs.append(conc)
        return sorted(concs, key=lambda x: x.valid_from_date_time)

    elif not expired and not mode:
        concs = list(Concession.objects.filter(customer_id=customer.id, valid_to_date_time__gt=today))
        for conc in linked_conc:
            if conc.valid_to_date_time > today:
                concs.append(conc)
        return sorted(concs, key=lambda x: x.valid_from_date_time)

    else:
        concs = list(Concession.objects.filter(customer_id=customer.id, valid_to_date_time__lt=today))
        for conc in linked_conc:
            if conc.valid_to_date_time < today:
                concs.append(conc)
        return sorted(concs, key=lambda x: x.valid_from_date_time)


def getUsage(user, filters=None):
    cust = Customer.objects.get(user=user)

    # Get the filters
    mode = filters.get("mode")
    startdate = filters.get("startdate")
    enddate = filters.get("enddate")
    # Filter with the mode if given
    if (mode != 'None') and (mode is not None):
        usages = Usage.objects.filter(customer=cust.id, mode=Mode.objects.get(short_desc=mode))
    else:
        usages = Usage.objects.filter(customer=cust.id)

    usages = usages.filter(travel_to__date_time__range=[str(startdate), str(enddate)]) \
        .union(usages.filter(travel_from__date_time__range=[str(startdate), str(enddate)])) \
        .union(usages.filter(travel_from__date_time__lte=startdate, travel_to__date_time__gte=enddate))

    linked_usages = Usage.objects.none()
    linked_usages = getPCU('http://127.0.0.1:8000/api/', 'usage/?format=json')
    usages = list(usages)
    if linked_usages:
        for usage in linked_usages:
            if (usage.travel_from.date_time < enddate) and (usage.travel_to.date_time >= startdate):
                usages.append(usage)

    return sorted(usages, key=lambda x: x.travel_from.date_time)


def getOperators():
    try:
        r = requests.get('https://cs20operator.herokuapp.com/api/operator/')
        catalogue = r.json()[0]["items"]
        out_list = ast.literal_eval(repr(catalogue).replace('-', '_'))
        return out_list
    except ConnectionError:
        return {"operators": {"null": "null"}}


def getPCU(url, pcu, token=None):
    try:
        cust = Customer.objects.get(user=User.objects.get(username='customer2'))
        r = requests.get(url + pcu)
        catalogue = r.json()
        out_list = ast.literal_eval(repr(catalogue).replace('-', '_'))
        objs = []
        for ticket in out_list:
            mode = Mode(id=ticket['mode']['id'], short_desc=ticket['mode']['short_desc'])
            operator = Operator(name='RETRIEVED OP', homepage=ticket['operator']['homepage'], api_url=ticket['operator']['api_url'], phone=ticket['operator']['phone'], email=ticket['operator']['email'])
            recordid = RecordID(id=ticket['id'])
            latlongfrom, loc_from, latlongto, loc_to = getLocs(pcu.split('/')[0], ticket)

            if pcu == "concession/?format=json":
                price = MonetaryValue(amount=ticket['transaction']['price']['amount'], currency=ticket['transaction']['price']['currency'])
                trans = Transaction(date_time=formatdt(ticket['transaction']['date_time']), reference=ticket['transaction']['reference'], payment_type=ticket['transaction']['payment_type'], payment_method=ticket['transaction']['payment_method'], price=price)
                disc = Discount(discount_type=ticket['discount']['discount_type'], discount_value=ticket['discount']['discount_value'], discount_description=ticket['discount']['discount_description'])
                concession = Concession(id=recordid, mode=mode, operator=operator, name=mode.short_desc, price=price, discount=disc,
                                        transaction=trans, valid_from_date_time=formatdt(ticket['valid_from_date_time']), valid_to_date_time=formatdt(ticket['valid_to_date_time']),
                                        conditions=ticket['conditions'], customer=cust)
                objs.append(concession)

            if pcu == "purchase/?format=json":
                price = MonetaryValue(amount=ticket['transaction']['price']['amount'], currency=ticket['transaction']['price']['currency'])
                tc = TravelClass(travel_class=ticket['travel_class'])
                trans = Transaction(date_time=formatdt(ticket['transaction']['date_time']), reference=ticket['transaction']['reference'], payment_type=ticket['transaction']['payment_type'], payment_method=ticket['transaction']['payment_method'], price=price)
                tick = Ticket(reference=ticket['ticket']['reference'], number_usages=ticket['ticket']['number_usages'], reference_type=ticket['ticket']['reference_type'], medium=ticket['ticket']['medium'])
                balance = MonetaryValue(amount=ticket['account_balance']['amount'], currency=ticket['account_balance']['currency'])
                vehicle = Vehicle(reference=ticket['vehicle']['reference'], vehicle_type=ticket['vehicle']['vehicle_type'])
                purchase = Purchase(id=recordid, mode=mode, operator=operator, travel_class=tc, booking_date_time=formatdt(ticket['booking_date_time']),
                                    transaction=trans, account_balance=balance, vehicle=vehicle, travel_from_date_time=formatdt(ticket['travel_from_date_time']),
                                    travel_to_date_time=formatdt(ticket['travel_to_date_time']), ticket=tick,
                                    location_from=loc_from, location_to=loc_to, customer=cust)
                objs.append(purchase)

            if pcu == "usage/?format=json":
                price = MonetaryValue(amount=ticket['price']['amount'], currency=ticket['price']['currency'])
                uft1 = UsageFromTo(location=loc_from, date_time=formatdt(ticket['travel_from']['date_time'], False), reference=ticket['travel_from']['reference'])
                uft2 = UsageFromTo(location=loc_to, date_time=formatdt(ticket['travel_to']['date_time'], False), reference=ticket['travel_from']['reference'])
                tc = TravelClass(travel_class=ticket['travel_class'])
                ur = UsageReference(reference=ticket['reference']['reference'], reference_type=ticket['reference']['reference_type'])
                tick = Ticket(reference=ticket['ticket']['reference'], number_usages=ticket['ticket']['number_usages'], reference_type=ticket['ticket']['reference_type'], medium=ticket['ticket']['medium'])
                usage = Usage(id=recordid, mode=mode, operator=operator, reference=ur, travel_class=tc,
                              travel_from=uft1, travel_to=uft2, ticket=tick, price=price, customer=cust)
                objs.append(usage)
        return objs
    except ConnectionError:
        return []
    except TypeError:
        return []


def getLocs(pcu, ticket):
    if pcu == 'concession':
        return [None, None, None, None]
    if pcu == 'usage':
        latlongfrom = LatitudeLongitude(latitude=ticket['travel_from']['location']['lat_long']['latitude'], longitude=ticket['travel_from']['location']['lat_long']['longitude'])
        loc_from = Location(lat_long=latlongfrom, NaPTAN=ticket['travel_from']['location']['NaPTAN'])
        latlongto = LatitudeLongitude(latitude=ticket['travel_to']['location']['lat_long']['latitude'], longitude=ticket['travel_to']['location']['lat_long']['longitude'])
        loc_to = Location(lat_long=latlongto, NaPTAN=ticket['travel_to']['location']['NaPTAN'])
    else:
        latlongfrom = LatitudeLongitude(latitude=ticket['location_from']['lat_long']['latitude'], longitude=ticket['location_from']['lat_long']['longitude'])
        loc_from = Location(lat_long=latlongfrom, NaPTAN=ticket['location_from']['NaPTAN'])
        latlongto = LatitudeLongitude(latitude=ticket['location_to']['lat_long']['latitude'], longitude=ticket['location_to']['lat_long']['longitude'])
        loc_to = Location(lat_long=latlongto, NaPTAN=ticket['location_to']['NaPTAN'])
    return [latlongfrom, loc_from, latlongto, loc_to]

def formatdt(time, nano=True):
    time = time.replace('_', '-')
    if nano and (len(time) > 20):
        time = datetime.datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=pytz.UTC)
        return time.replace(microsecond=0)
    else:
        return datetime.datetime.strptime(time, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.UTC)