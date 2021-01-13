import os, random, csv, datetime, pytz
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'customer.settings')
from django.contrib.auth.hashers import make_password

import django
django.setup()

import decimal
import datetime

from django.contrib.auth.models import User
from website.models import *
from django.utils.timezone import make_aware

times = [random.randint(-90,90) for i in range(1000)]

def randtime(order, no, pos=None):
    if pos:
        if order == 1:
            return django.utils.timezone.now()+datetime.timedelta(days=times[pos])
        else:
            return django.utils.timezone.now() + datetime.timedelta(days=times[pos]+30)
    if order == 1:
        return django.utils.timezone.now()+datetime.timedelta(days=random.randint(0, no))
    else:
        return django.utils.timezone.now()+datetime.timedelta(days=random.randint(no, no*2))


def populate():

    # delete data if the database is already populated
    if User.objects.filter(username='dev').exists():
        User.objects.all().delete()
    if Customer.objects.all():
        Customer.objects.all().delete()
    if Account.objects.all():
        Account.objects.all().delete()
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

    # superuser account - use this to log into the django admin page
    dev = User.objects.create_user(username='dev', password='1234', is_superuser=True, is_staff=True, email="dev@project.com", first_name='dev')

    # general stuff
    train, created = Mode.objects.get_or_create(id="train", short_desc="Train")
    bus, created = Mode.objects.get_or_create(id="bus", short_desc="Bus")
    tram, created = Mode.objects.get_or_create(id="tram", short_desc="Tram")
    vehicle_type, created = Vehicle.objects.get_or_create(reference="train 3001", vehicle_type="train")

    modes = [train, bus, tram]
    #create latlongs and location
    locsnum = 400
    exists = []
    with open('extra/gb.csv') as csvfile:
        reader = list(csv.reader(csvfile, delimiter=',', quotechar='|'))
        for i in range(locsnum):
            unique = False
            while not unique:
                loc = random.randint(1, 400)
                new_loc = reader[loc][0], reader[loc][1], reader[loc][2]
                if new_loc not in exists:
                    exists.append(new_loc)
                    unique = True
    latlongs = LatitudeLongitude.objects.bulk_create([LatitudeLongitude(latitude=exists[i][1], longitude=exists[i][2]) for i in range(locsnum)])
    latlongs = LatitudeLongitude.objects.all()
    Location.objects.bulk_create([Location(lat_long=latlongs[i], NaPTAN="idk", name=exists[i][0]) for i in range(locsnum)])
    locations = list(Location.objects.all())

    #create usagefromto
    usagetimes = []
    for i in range(locsnum//2):
        time1 = random.randint(1420070400, 1577836800)
        time2 = time1 + random.randint(0,18000)
        usagetimes.append(datetime.datetime.fromtimestamp(time1, pytz.UTC))
        usagetimes.append(datetime.datetime.fromtimestamp(time2, pytz.UTC))
    UsageFromTo.objects.bulk_create([UsageFromTo(location=locations[i], date_time=usagetimes[i], reference="reference usage") for i in range(locsnum)])
    UFT = list(UsageFromTo.objects.all())

    #create usagereference
    UsageReference.objects.bulk_create([UsageReference(reference=i, reference_type='usage type') for i in range(locsnum)])
    URs = list(UsageReference.objects.all())

    #create discount
    Discount.objects.get_or_create(discount_type="Young person", discount_value="0.20", discount_description="16-25 Railcard")
    Discount.objects.get_or_create(discount_type="Pensioner", discount_value="0.40", discount_description="Pensioner Travelcard")
    Discount.objects.get_or_create(discount_type="Middle person", discount_value="0.30", discount_description="Middle-age Buspass")
    discounts = list(Discount.objects.all())


    customerno = 6
    #create customers and users
    User.objects.bulk_create([User(username='customer'+str(i), password=make_password('1234', None, 'md5'), email='customer'+str(i)+'@scotrail.co.uk.', first_name='Customer '+ str(i)) for i in range(customerno)])
    users = User.objects.all()
    Customer.objects.bulk_create([Customer(user=i) for i in users])
    customers = Customer.objects.all()

    #create account
    operators = ["ScotRail", "CityLink", "FirstBus", "Zebras"]
    Account.objects.bulk_create([Account(customer=customer, operator_id=random.choice(operators)) for customer in customers])

    #create travelclass
    TravelClass.objects.get_or_create(travel_class="First Class")
    TravelClass.objects.get_or_create(travel_class="Second Class")
    TravelClass.objects.get_or_create(travel_class="Economy")

    classes = TravelClass.objects.all()

    mvn = 800
    #create monetary value
    MonetaryValue.objects.bulk_create([MonetaryValue(amount=random.randint(0,10), currency="GBP", symbol="£") for i in range(mvn)])
    mvns = list(MonetaryValue.objects.all())

    #create transactions
    Transaction.objects.bulk_create([Transaction(date_time=random.choice(usagetimes), payment_type="Visa", payment_method="Debit", price=mvns[i]) for i in range(mvn)])
    trans = list(Transaction.objects.all())

    #create recordID
    recordno = 360
    RecordID.objects.bulk_create([RecordID(id=str(i)) for i in range(recordno)])
    records = list(RecordID.objects.all())

    #create ticket
    Ticket.objects.bulk_create([Ticket(reference="GLASGOW-STIRLING"+str(i), number_usages="0", reference_type="Idk", medium="Idk 2") for i in range(locsnum)])
    tickets = Ticket.objects.all()
    #create concessions
    modelist = [modes[i%3] for i in range(0, recordno)]
    random.shuffle(modelist)
    Concession.objects.bulk_create([Concession(id=records.pop(), mode=modelist[i], name=modelist[i].short_desc,
                                     price=mvns.pop(), discount=random.choice(discounts),
                                     transaction=trans.pop(),
                                     valid_from_date_time=randtime(1, 45, i),
                                     valid_to_date_time=randtime(2, 1, i),
                                     conditions="Below 25", customer=customers[i%3]) for i in range(0, recordno//3)])

    cons = list(Concession.objects.all())

    #create purchases
    curtime = django.utils.timezone.now()
    Purchase.objects.bulk_create([Purchase(id=records.pop(), mode=random.choice(modes), travel_class=random.choice(classes), booking_date_time=django.utils.timezone.now(),
                                 transaction=trans.pop(),
                                 account_balance=mvns.pop(),
                                 vehicle=vehicle_type,
                                 travel_from_date_time=randtime(1,45),
                                 travel_to_date_time=randtime(2,45),
                                 concession=cons.pop(), ticket=tickets[i],
                                 location_from=locations.pop(), location_to=locations.pop(), customer=customers[i%3]) for i in range(recordno//3, 2*recordno//3)])
    purchases = list(Purchase.objects.all())

    Usage.objects.bulk_create([Usage(id=records.pop(), mode=random.choice(modes), reference=URs[i],
                                      travel_class=random.choice(classes), travel_from=UFT.pop(),
                                      travel_to=UFT.pop(), purchase_id=purchases.pop(),
                                      ticket_reference=tickets[i], price=mvns.pop(),
                                      customer=customers[i%3]) for i in range(2*recordno//3, recordno)])


if __name__ == '__main__':
    print('Starting population script...', end="")
    populate()
    print('DONE')