import os, random
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'customer.settings')

import django
django.setup()

import decimal 
import datetime
from django.contrib.auth.models import User
from website.models import *
from django.utils.timezone import make_aware
from website.helper_functions import emptyDatabase

def populate():  

    emptyDatabase()

    # create superuser account - use this to log into the django admin page
    dev = User.objects.create_user(username='dev2', password='1234', is_superuser=True, is_staff=True, email="dev2@project.com", first_name='dev2')

    # create modes
    train, created = Mode.objects.get_or_create(id="train", short_desc="Train")
    bus, created = Mode.objects.get_or_create(id="bus", short_desc="Bus")
    tram, created = Mode.objects.get_or_create(id="tram", short_desc="Tram")
    
    first_class, created = TravelClass.objects.get_or_create(travel_class="First Class")
    vehicle_type, created = Vehicle.objects.get_or_create(reference="train 4001", vehicle_type="train")
    
    # create Cheetahs operator
    cheetahs, created = Operator.objects.get_or_create(admin=dev, name="Cheetahs", homepage="http://127.0.0.1:8002/", api_url="http://127.0.0.1:8002/api/", phone="0394098748", email="bigemail@domain.com")
    modes = [train, bus, tram]
    cheetahs.modes.set(modes)

    # create customer 1
    user1 = User.objects.create_user(username='customer1.1', password='1234', email='customer@cheetahs.co.uk.', first_name='Cheetahs Customer')
    customer1, created = Customer.objects.get_or_create(user=user1, operator=cheetahs)

    # add a concession to the customer1 account
    record1, created = RecordID.objects.get_or_create(id="0000100")
    price1, created = MonetaryValue.objects.get_or_create(amount="30.00", currency="GBP", symbol="£")
    transaction1, created = Transaction.objects.get_or_create(payment_type="Card", payment_method="Visa Debit", price=price1)
    discount1, created = Discount.objects.get_or_create(discount_type="Amount", discount_value="5.00", discount_description="16-25 Railcard")
    concession1, created = Concession.objects.get_or_create(id=record1, mode=train, operator=cheetahs, name="16-25 Railcard", price=price1, discount=discount1, transaction=transaction1, valid_from_date_time=django.utils.timezone.now(), valid_to_date_time=django.utils.timezone.now()+datetime.timedelta(days=728), conditions="Below 25", customer=customer1)

    # add a second concession to the customer1 account
    record7, created = RecordID.objects.get_or_create(id="0000107")
    price7, created = MonetaryValue.objects.get_or_create(amount="7.00", currency="GBP", symbol="£")
    transaction7, created = Transaction.objects.get_or_create(payment_type="Card", payment_method="Visa Debit", price=price7)
    discount7, created = Discount.objects.get_or_create(discount_type="%", discount_value="15.00", discount_description="Student Railcard")
    concession7, created = Concession.objects.get_or_create(id=record7, mode=bus, operator=cheetahs, name="Student Railcard", price=price7, discount=discount7, transaction=transaction7, valid_from_date_time=django.utils.timezone.now(), valid_to_date_time=django.utils.timezone.now()+datetime.timedelta(days=728), conditions="Student", customer=customer1)

    # add a purchase to the customer1 account (30 days from now)
    record2, created = RecordID.objects.get_or_create(id="00000102")
    price2, created = MonetaryValue.objects.get_or_create(amount="12.49", currency="GBP", symbol="£")
    transaction2, created = Transaction.objects.get_or_create(payment_type="Card", payment_method="Visa Debit", price=price2)
    account_balance2, created = MonetaryValue.objects.get_or_create(amount="100.00", currency="GBP", symbol="£")
    ticket2, created = Ticket.objects.get_or_create(reference="GLASGOW CENTRAL-OBAN", number_usages="0", reference_type="Idk", medium="Idk 2")
    coordinates_from2, created = LatitudeLongitude.objects.get_or_create(latitude=decimal.Decimal(55.8591), longitude=decimal.Decimal(4.2581))
    location_from2, created = Location.objects.get_or_create(lat_long=coordinates_from2, NaPTAN="idk", other="Glasgow", name="Glasgow Central")
    coordinates_to2, created = LatitudeLongitude.objects.get_or_create(latitude=decimal.Decimal(56.4125), longitude=decimal.Decimal(5.4740))
    location_to2, created = Location.objects.get_or_create(lat_long=coordinates_to2, NaPTAN="idk", other="Oban", name="Oban")
    purchase2, created = Purchase.objects.get_or_create(id=record2, mode=train, operator=cheetahs, travel_class=first_class, booking_date_time=django.utils.timezone.now(), transaction=transaction2, account_balance=account_balance2, vehicle=vehicle_type, travel_from_date_time=django.utils.timezone.now(), travel_to_date_time=django.utils.timezone.now()+datetime.timedelta(days=30), concession=concession1, ticket=ticket2, location_from=location_from2, location_to=location_to2, customer=customer1)

    # add a second purchase to the customer1 account (30 days ago)
    record8, created = RecordID.objects.get_or_create(id="00000108")
    price8, created = MonetaryValue.objects.get_or_create(amount="9.50", currency="GBP", symbol="£")
    transaction8, created = Transaction.objects.get_or_create(payment_type="Card", payment_method="Visa Debit", price=price8)
    account_balance8, created = MonetaryValue.objects.get_or_create(amount="100.00", currency="GBP", symbol="£")
    ticket8, created = Ticket.objects.get_or_create(reference="EDINBURGH WAVERLEY-GLASGOW QUEEN STREET", number_usages="0", reference_type="Idk", medium="Idk 2")
    coordinates_from8, created = LatitudeLongitude.objects.get_or_create(latitude=decimal.Decimal(55.9520), longitude=decimal.Decimal(3.1900))
    location_from8, created = Location.objects.get_or_create(lat_long=coordinates_from8, NaPTAN="idk", other="Edinburgh", name="Edinburgh Waverley")
    coordinates_to8, created = LatitudeLongitude.objects.get_or_create(latitude=decimal.Decimal(55.8625), longitude=decimal.Decimal(4.2512))
    location_to8, created = Location.objects.get_or_create(lat_long=coordinates_to8, NaPTAN="idk", other="Glasgow", name="Glasgow Queen Street")
    purchase8, created = Purchase.objects.get_or_create(id=record8, mode=bus, operator=cheetahs, travel_class=first_class, booking_date_time=django.utils.timezone.now(), transaction=transaction8, account_balance=account_balance8, vehicle=vehicle_type, travel_from_date_time=django.utils.timezone.now()-datetime.timedelta(days=30), travel_to_date_time=django.utils.timezone.now(), concession=concession1, ticket=ticket8, location_from=location_from8, location_to=location_to8, customer=customer1)

    # add a third purchase to the customer1 account (10 days ago - 10 days from now)
    record9, created = RecordID.objects.get_or_create(id="00000109")
    price9, created = MonetaryValue.objects.get_or_create(amount="11.25", currency="GBP", symbol="£")
    transaction9, created = Transaction.objects.get_or_create(payment_type="Card", payment_method="Visa Debit", price=price9)
    account_balance9, created = MonetaryValue.objects.get_or_create(amount="100.00", currency="GBP", symbol="£")
    ticket9, created = Ticket.objects.get_or_create(reference="INVERNESS-PERTH", number_usages="0", reference_type="Idk", medium="Idk 2")
    coordinates_from9, created = LatitudeLongitude.objects.get_or_create(latitude=decimal.Decimal(57.4798), longitude=decimal.Decimal(4.2235))
    location_from9, created = Location.objects.get_or_create(lat_long=coordinates_from9, NaPTAN="idk", name="Inverness")
    coordinates_to9, created = LatitudeLongitude.objects.get_or_create(latitude=decimal.Decimal(56.3917), longitude=decimal.Decimal(3.4384))
    location_to9, created = Location.objects.get_or_create(lat_long=coordinates_to9, NaPTAN="idk", other="Perth", name="Perth")
    purchase9, created = Purchase.objects.get_or_create(id=record9, mode=tram, operator=cheetahs, travel_class=first_class, booking_date_time=django.utils.timezone.now(), transaction=transaction9, account_balance=account_balance9, vehicle=vehicle_type, travel_from_date_time=django.utils.timezone.now()-datetime.timedelta(days=10), travel_to_date_time=django.utils.timezone.now()+datetime.timedelta(days=10), concession=concession1, ticket=ticket9, location_from=location_from9, location_to=location_to9, customer=customer1)


    # add a usage to the customer1 account
    record3, created = RecordID.objects.get_or_create(id="00000103")
    usage_reference3, created = UsageReference.objects.get_or_create(reference="011", reference_type="usage type")

    coordinates_to3, created = LatitudeLongitude.objects.get_or_create(latitude=decimal.Decimal(55.7932), longitude=decimal.Decimal(4.8673))
    location_to3, created = Location.objects.get_or_create(lat_long=coordinates_to3, NaPTAN="idk", other="Largs", name="Largs")
    travel_to3, created = UsageFromTo.objects.get_or_create(location=location_to3, date_time=django.utils.timezone.now(), reference="reference usage")

    coordinates_from3, created = LatitudeLongitude.objects.get_or_create(latitude=decimal.Decimal(55.6396), longitude=decimal.Decimal(4.8205))
    location_from3, created = Location.objects.get_or_create(lat_long=coordinates_from3, NaPTAN="idk", other="Ardrossan", name="Ardrossan")
    travel_from3, created = UsageFromTo.objects.get_or_create(location=location_from3, date_time=django.utils.timezone.now()-datetime.timedelta(days=10), reference="reference usage")

    usage3, created = Usage.objects.get_or_create(id=record3, mode=train, operator=cheetahs, reference=usage_reference3, travel_class=first_class, travel_from=travel_from3, travel_to=travel_to3, purchase_id=purchase2, ticket=ticket2, price=price2, customer=customer1)

    # add a second usage to the customer1 account
    record10, created = RecordID.objects.get_or_create(id="00000110")
    usage_reference10, created = UsageReference.objects.get_or_create(reference="020", reference_type="usage type")

    coordinates_to10, created = LatitudeLongitude.objects.get_or_create(latitude=decimal.Decimal(56.8204), longitude=decimal.Decimal(5.1061))
    location_to10, created = Location.objects.get_or_create(lat_long=coordinates_to10, NaPTAN="idk", other="Fort William", name="Fort William")
    travel_to10, created = UsageFromTo.objects.get_or_create(location=location_to10, date_time=django.utils.timezone.now(), reference="reference usage")

    coordinates_from10, created = LatitudeLongitude.objects.get_or_create(latitude=decimal.Decimal(56.3905), longitude=decimal.Decimal(4.6184))
    location_from10, created = Location.objects.get_or_create(lat_long=coordinates_from10, NaPTAN="idk", other="Crianlarich", name="Ciranlarich")
    travel_from10, created = UsageFromTo.objects.get_or_create(location=location_from10, date_time=django.utils.timezone.now()-datetime.timedelta(days=10), reference="reference usage")

    usage10, created = Usage.objects.get_or_create(id=record10, mode=bus, operator=cheetahs, reference=usage_reference10, travel_class=first_class, travel_from=travel_from10, travel_to=travel_to10, purchase_id=purchase8, ticket=ticket8, price=price8, customer=customer1)

    # create customer 2
    user2 = User.objects.create_user(username='customer2.1', password='1234', email='cheetahs2@scotrail.co.uk.', first_name='Cheetahs Customer Two')
    customer2, created = Customer.objects.get_or_create(user=user2, operator=cheetahs)

    # add a concession to the customer2 account
    record6, created = RecordID.objects.get_or_create(id="00000106")
    price6, created = MonetaryValue.objects.get_or_create(amount="10.30", currency="GBP", symbol="£")
    transaction6, created = Transaction.objects.get_or_create(payment_type="Card", payment_method="Visa Debit", price=price6)
    discount6, created = Discount.objects.get_or_create(discount_type="%", discount_value="55", discount_description="Over 60 yrs")
    concession6, created = Concession.objects.get_or_create(id=record6, mode=train, operator=cheetahs, name="Senior Traveller", price=price6, discount=discount6, transaction=transaction6, valid_from_date_time=django.utils.timezone.now(), valid_to_date_time=django.utils.timezone.now()+datetime.timedelta(days=364), conditions="Over 60", customer=customer2)

    # add a purchase to the customer2 account
    record4, created = RecordID.objects.get_or_create(id="00000104")
    price4, created = MonetaryValue.objects.get_or_create(amount="15.60", currency="GBP", symbol="£")
    transaction4, created = Transaction.objects.get_or_create(payment_type="Card", payment_method="Visa Debit", price=price4)
    account_balance4, created = MonetaryValue.objects.get_or_create(amount="50.00", currency="GBP", symbol="£")
    ticket4, created = Ticket.objects.get_or_create(reference="AVIEMORE-THURSO", number_usages="0", reference_type="Idk", medium="Idk 2")
    coordinates_from4, created = LatitudeLongitude.objects.get_or_create(latitude=decimal.Decimal(57.1893), longitude=decimal.Decimal(3.8285))
    location_from4, created = Location.objects.get_or_create(lat_long=coordinates_from4, NaPTAN="idk", name="Aviemore")
    coordinates_to4, created = LatitudeLongitude.objects.get_or_create(latitude=decimal.Decimal(58.5902), longitude=decimal.Decimal(3.5276))
    location_to4, created = Location.objects.get_or_create(lat_long=coordinates_to4, NaPTAN="idk", name="Thurso")
    purchase4, created = Purchase.objects.get_or_create(id=record4, mode=train, operator=cheetahs, travel_class=first_class, booking_date_time=django.utils.timezone.now(), transaction=transaction4, account_balance=account_balance4, vehicle=vehicle_type, travel_from_date_time=django.utils.timezone.now(), travel_to_date_time=django.utils.timezone.now()+datetime.timedelta(days=30), concession=concession6, ticket=ticket4, location_from=location_from4, location_to=location_to4, customer=customer2)

    # add a usage to the customer2 account
    record5, created = RecordID.objects.get_or_create(id="00000105")
    usage_reference5, created = UsageReference.objects.get_or_create(reference="012", reference_type="usage type")

    coordinates_to5, created = LatitudeLongitude.objects.get_or_create(latitude=decimal.Decimal(55.8641), longitude=decimal.Decimal(3.9818))
    location_to5, created = Location.objects.get_or_create(lat_long=coordinates_to5, NaPTAN="idk", name="Airdrie")
    travel_to5, created = UsageFromTo.objects.get_or_create(location=location_to5, date_time=django.utils.timezone.now(), reference="reference usage")

    coordinates_from5, created = LatitudeLongitude.objects.get_or_create(latitude=decimal.Decimal(56.0024), longitude=decimal.Decimal(4.5834))
    location_from5, created = Location.objects.get_or_create(lat_long=coordinates_from5, NaPTAN="idk", name="Balloch")
    travel_from5, created = UsageFromTo.objects.get_or_create(location=location_from5, date_time=django.utils.timezone.now()+datetime.timedelta(days=5), reference="reference usage")

    usage5, created = Usage.objects.get_or_create(id=record5, mode=train, operator=cheetahs, reference=usage_reference5, travel_class=first_class, travel_from=travel_from5, travel_to=travel_to5, purchase_id=purchase4, ticket=ticket4, price=price4, customer=customer2)

if __name__ == '__main__':
    print('Starting population script...', end="")
    populate()
    print('DONE')