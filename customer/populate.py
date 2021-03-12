import os, random, csv, datetime, pytz, decimal
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'customer.settings')
from django.contrib.auth.hashers import make_password

import django
django.setup()

from django.contrib.auth.models import User
from website.models import *
from django.utils.timezone import make_aware
from website.helper_functions import emptyDatabase

times = [random.randint(-90,90) for i in range(1000)]

# Returns a random time within a certain interval depending on the arguments
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

    ##################### Operator Parameters #####################
    opname = "Zebras"
    modenames = ["cycle", "motorbike"]
    ophomepage = "https://cs20customer.herokuapp.com/"
    opapiurl = "https://cs20customer.herokuapp.com/api/"
    
    specific_from_date_time = datetime.datetime(2021,3,24,hour=16,minute=30).replace(tzinfo=pytz.UTC)
    specific_to_date_time = datetime.datetime(2021,3,24,hour=17,minute=30).replace(tzinfo=pytz.UTC)
    specific_from_loc_index = 200
    specific_to_loc_index = 96
    specific_mode_id = modenames[0]
    specific_username = "customer0"
    ###############################################################

    emptyDatabase()

    # create superuser account - use this to log into the django admin page
    dev = User.objects.create_user(username='dev', password='1234', is_superuser=True, is_staff=True, email="dev@project.com", first_name='dev')

    # create modes
    for m in modenames:
        Mode.objects.get_or_create(id=m, short_desc=m.capitalize())
    modes = list(Mode.objects.all())
    
    vehicle_type, created = Vehicle.objects.get_or_create(reference="boat 3001", vehicle_type="boat")
    
    # create this operator
    thisop, created = Operator.objects.get_or_create(admin=dev, name=opname, homepage=ophomepage, api_url=opapiurl, phone="0394098748", email="thisop@bossman.com")
    thisop.modes.set(modes)

    # create latlongs and location, read from a csv file containing UK location details
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
    locations2 = list(Location.objects.all())
    
    # create usagefromto
    usagetimes = []
    for i in range(locsnum//2):
        time1 = random.randint(1420070400, 1577836800)
        time2 = time1 + random.randint(0,18000)
        usagetimes.append(datetime.datetime.fromtimestamp(time1, pytz.UTC))
        usagetimes.append(datetime.datetime.fromtimestamp(time2, pytz.UTC))
    UsageFromTo.objects.bulk_create([UsageFromTo(location=locations[i], date_time=usagetimes[i], reference="reference usage") for i in range(locsnum)])
    UFT = list(UsageFromTo.objects.all())
    UFT.reverse()

    # create usagereference
    UsageReference.objects.bulk_create([UsageReference(reference=i, reference_type='usage type') for i in range(locsnum)])
    URs = list(UsageReference.objects.all())

    # create discount
    Discount.objects.get_or_create(discount_type="Young person", discount_value="50", discount_description="Under 19's Pass")
    Discount.objects.get_or_create(discount_type="Pensioner", discount_value="40", discount_description="Pensioner Travelcard")
    Discount.objects.get_or_create(discount_type="Middle person", discount_value="20", discount_description="Water Concession")
    discounts = list(Discount.objects.all())

    # create customers and users
    customerno = 6
    User.objects.bulk_create([User(username='customer'+str(i), password=make_password('1234', None, 'md5'), email='customer'+str(i)+'customer'+str(i)+'.co.uk.', first_name='Customer '+ str(i)) for i in range(customerno)])
    users = User.objects.all()
    Customer.objects.bulk_create([Customer(user=i, operator=thisop) for i in users])
    customers = Customer.objects.all()

    # create travelclass
    TravelClass.objects.get_or_create(travel_class="First Class")
    TravelClass.objects.get_or_create(travel_class="Second Class")
    TravelClass.objects.get_or_create(travel_class="Economy")
    classes = TravelClass.objects.all()

    # create monetary value
    mvn = 800
    MonetaryValue.objects.bulk_create([MonetaryValue(amount=random.randint(0,10), currency="GBP", symbol="£") for i in range(mvn)])
    mvns = list(MonetaryValue.objects.all())

    # create transactions
    Transaction.objects.bulk_create([Transaction(date_time=random.choice(usagetimes), reference="Ref"+str(i), payment_type="Card", payment_method="Visa Debit", price=mvns[i]) for i in range(mvn)])
    trans = list(Transaction.objects.all())

    # create recordID
    recordno = 90
    RecordID.objects.bulk_create([RecordID(id=str(i)) for i in range(recordno)])
    records = list(RecordID.objects.all())

    # create tickets
    Ticket.objects.bulk_create([Ticket(reference="Ticket Reference " + str(i), number_usages="0", reference_type="ITSO ISRN", medium="Smart card") for i in range(locsnum)])
    tickets = Ticket.objects.all()
    
    # create concessions
    modelist = [modes[i%2] for i in range(0, recordno)]
    random.shuffle(modelist)
    Concession.objects.bulk_create([Concession(id=records.pop(), mode=modelist[i], operator=thisop, name=discounts[i%3].discount_description,
                                     price=mvns.pop(), discount=discounts[i%3],
                                     transaction=trans.pop(),
                                     valid_from_date_time=randtime(1, 45, i),
                                     valid_to_date_time=randtime(2, 1, i),
                                     conditions="Below 25", customer=customers[i%len(customers)]) for i in range(0, recordno//3)])

    cons = list(Concession.objects.all())

    # create purchases
    curtime = django.utils.timezone.now()
    Purchase.objects.bulk_create([Purchase(id=records.pop(), mode=random.choice(modes), operator=thisop, travel_class=random.choice(classes), booking_date_time=django.utils.timezone.now(),
                                 transaction=trans.pop(),
                                 account_balance=mvns.pop(),
                                 vehicle=vehicle_type,
                                 travel_from_date_time=randtime(1,45),
                                 travel_to_date_time=randtime(2,45),
                                 concession=cons.pop(), ticket=tickets[i],
                                 location_from=locations.pop(), location_to=locations.pop(), customer=customers[i%len(customers)]) for i in range(recordno//3, 2*recordno//3)])
    purchases = list(Purchase.objects.all())

    # create usages
    Usage.objects.bulk_create([Usage(id=records.pop(), mode=random.choice(modes), operator=thisop, reference=URs[i],
                                      travel_class=random.choice(classes), travel_from=UFT.pop(),
                                      travel_to=UFT.pop(), purchase_id=purchases.pop(),
                                      ticket=tickets[i], price=mvns.pop(),
                                      customer=customers[i%len(customers)]) for i in range(2*recordno//3, recordno)])

    # add some services
    usages = list(Usage.objects.all())
    Service.objects.bulk_create([Service(service_type="Charging", unit="KwH", amount=20, price=mvns.pop(), usage_id=usages[i]) for i in range(recordno//6)])

    # Add a Usage for a specific date - to demonstrate journey grouping
    specific_customer = Customer.objects.get(user__username=specific_username)
    specific_from_lat_long = LatitudeLongitude.objects.create(latitude=reader[specific_from_loc_index][1], longitude=reader[specific_from_loc_index][2])
    specific_to_lat_long = LatitudeLongitude.objects.create(latitude=reader[specific_to_loc_index][1], longitude=reader[specific_to_loc_index][2])
    Usage.objects.create(id=RecordID.objects.create(id="9001"),
                         mode=Mode.objects.get(id=specific_mode_id),
                         operator=thisop,
                         reference=UsageReference.objects.create(reference=8000, reference_type='usage ref'),
                         travel_class=TravelClass.objects.get(travel_class="Economy"),
                         travel_from=UsageFromTo.objects.create(location=Location.objects.create(lat_long=specific_from_lat_long, NaPTAN="idk", name=reader[specific_from_loc_index][0]), date_time=specific_from_date_time, reference="from ref"),
                         travel_to=UsageFromTo.objects.create(location=Location.objects.create(lat_long=specific_to_lat_long, NaPTAN="idk", name=reader[specific_to_loc_index][0]), date_time=specific_to_date_time, reference="to ref"),
                         purchase_id = Purchase.objects.filter(customer=specific_customer)[0],
                         ticket=Ticket.objects.create(reference="Ticket Ref 314", number_usages="1", reference_type="ITSO ISRN", medium="Smart card"),
                         price=mvns.pop(),
                         customer=specific_customer)


if __name__ == '__main__':
    print('Starting population script...', end="")
    populate()
    print('DONE')