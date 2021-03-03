import sys
sys.path.append("..")

from .models import *
import datetime
from django.utils import timezone
import pytz
import requests
from requests.exceptions import ConnectionError
import ast
from requests.auth import HTTPBasicAuth
import json
import extra.reverse_geocode as reverse_geocode

client_id = "ou9h2JlNWlch0Vj7N2AzK6qYANdNIl1Mo7gg1oZj"
client_secret = "5EUIoebBH2SxgjANJ6KL1q1GcGZn924OCQbhbysqQ9kb79W3i9YBDGbMGlYw1NPee40fI3t0OYFW2zaghGl5buKfUzGQc7XuibqpbA296LKNiWWuF02RUUBaDAydV7t9"


# Returns all modes of transport in a given list of Purchases/Concessions/Usages
def getModes(tickets=[]):
    local_modes = set(Mode.objects.all())

    # Here we also get the unique Modes offered by linked Operators by extracting them from the tickets
    linked_modes = set([t.mode for t in tickets])

    # Return all modes of transport offered by this Operator and linked Operators
    modes = list(local_modes.union(linked_modes))
    return modes


# Returns the Purchases of the given user, filtered by the given dates and mode of transport
def getPurchases(user, filters={}):
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
def getConcessions(user, context={}):
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
    status = context.get('status', "all")
    mode = context.get('mode')
    
    # Filter by mode
    if mode and mode != "None":
        local_concessions = [c for c in local_concessions if c.mode.short_desc == mode]
        
    # Filter by status (valid or expired)
    if status == "past":
        local_concessions = [c for c in local_concessions if c.valid_to_date_time < today]
    elif status == "all":
        pass
    else:
        local_concessions = [c for c in local_concessions if c.valid_to_date_time > today]
        
    # Return the user's Concessions sorted by valid_from_date_time
    return sorted(local_concessions, key=lambda x: x.valid_from_date_time)


# Returns the Usages of the given user, filtered by the given dates and mode of transport
def getUsage(user, filters={}):
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
def getOperators(opid=""):
    try:
        if opid:
            opid = ('?filterString=' + opid)
        r = requests.get('https://cs20operator.herokuapp.com/api/operator/' + opid)
        catalogue = r.json()[0]["items"]
        out_list = ast.literal_eval(repr(catalogue).replace('-', '_'))
        operators = []
        for operator in out_list:
            op = {'href': operator['href']}
            metadata = operator['item_metadata']
            op['name'] = getRelValue(metadata, 'hasDescription')
            op['homepage'] = getRelValue(metadata, 'hasHomepage')
            op['id'] = getRelValue(metadata, 'hasID')
            op['email'] = getRelValue(metadata, 'hasEmail')
            op['phone'] = getRelValue(metadata, 'hasPhone')
            op['language'] = getRelValue(metadata, 'hasDefaultLanguage')
            op['numbermodes'] = int(getRelValue(metadata, 'hasNumberModes'))
            modeDict = {}
            for modeNo in range(op['numbermodes']):
                modeNo+= 1
                modeDict['mode'+str(modeNo)+'id'] = getRelValue(metadata, 'hasNumberMode'+str(modeNo)+'#Code')
                modeDict['mode' + str(modeNo) + 'desc'] = getRelValue(metadata, 'hasNumberMode' + str(modeNo) + '#Description')
            op['modes'] = modeDict
            operators.append(op)
        return operators
    except ConnectionError:
        return {"operators": {"null": "null"}}


def getRelValue(operatorData, relation):
    return [field['val'] for field in operatorData if relation in field['rel']][0]

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
                    concession = getTicketConcession(ticket, mode, operator, recordid, cust)
                    objs.append(concession)

                elif (api_endpoint == "purchase"):
                    purchase = getTicketPurchase(ticket, mode, operator, recordid, cust, loc_from, loc_to)
                    objs.append(purchase)

                elif (api_endpoint == "usage"):
                    usage = getTicketUsage(ticket, mode, operator, recordid, cust, loc_from, loc_to)
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

        op = getOperators(str(linked_account.operator_id))[0]
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
        

def getTicketPurchase(ticket, mode, operator, recordid, cust, loc_from, loc_to):
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


def getTicketConcession(ticket, mode, operator, recordid, cust):
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
    return concession


def getTicketUsage(ticket, mode, operator, recordid, cust, loc_from, loc_to):
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
    return tick


def getDiscount(ticket):
    discount_type = ticket['discount_type']
    discount_value = ticket['discount_value']
    discount_description = ticket['discount_description']
    disc = Discount(discount_type=discount_type, discount_value=discount_value,
                    discount_description=discount_description)
    return disc

def getVehicle(ticket):
    reference = ticket['reference']
    vehicle_type = ticket['vehicle_type']
    return Vehicle(reference=reference, vehicle_type=vehicle_type)


def getReference(ticket):
    reference = ticket['reference']
    reference_type = ticket ['reference_type']
    return UsageReference(reference=reference, reference_type=reference_type)

def getApi(endpoint):
    endpoints = ['purchase', 'concession', 'usage']

    for i in endpoint.split('/'):
        if i in endpoints:
            return i
    