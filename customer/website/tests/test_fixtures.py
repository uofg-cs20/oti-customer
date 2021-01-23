import random

import decimal 
import datetime

import django

from django.contrib.auth.models import User
from website.models import *
from django.utils.timezone import make_aware

def populate():

    # delete data if the database is already populated
    if User.objects.filter(username='customer0').exists():
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

    # general stuff
    train, created = Mode.objects.get_or_create(id="train", short_desc="Train")
    bus, created = Mode.objects.get_or_create(id="bus", short_desc="Bus")
    tram, created = Mode.objects.get_or_create(id="tram", short_desc="Tram")
    first_class, created = TravelClass.objects.get_or_create(travel_class="First Class")
    vehicle_type, created = Vehicle.objects.get_or_create(reference="train 3001", vehicle_type="train")
    
    # create user 1
    user1 = User.objects.create_user(username='customer0', password='1234', email='customer@scotrail.co.uk.', first_name='Customer One')
    
    # create Zebras operator
    zebras, created = Operator.objects.get_or_create(admin=user1, name="Zebras", homepage="http://127.0.0.1:8000/", api_url="http://127.0.0.1:8000/api/", phone="0394098748", email="bigemail@domain.com")
    modes = [train, bus, tram]
    zebras.modes.set(modes)
    
    # create customer 1
    customer1, created = Customer.objects.get_or_create(user=user1, operator=zebras)

    # add a concession purchase to the customer1 account
    record1, created = RecordID.objects.get_or_create(id="00000001")
    price1, created = MonetaryValue.objects.get_or_create(amount="30.00", currency="GBP", symbol="£")
    transaction1, created = Transaction.objects.get_or_create(payment_type="Visa", payment_method="Debit", price=price1)
    discount1, created = Discount.objects.get_or_create(discount_type="Young person", discount_value="0.20", discount_description="16-25 Railcard")
    concession1, created = Concession.objects.get_or_create(id=record1, mode=train, operator=zebras, name="16-25 Railcard", price=price1, discount=discount1, transaction=transaction1, valid_from_date_time=django.utils.timezone.now(), valid_to_date_time=django.utils.timezone.now()+datetime.timedelta(days=728), conditions="Below 25", customer=customer1)

    # add a second concession purchase to the customer1 account
    record7, created = RecordID.objects.get_or_create(id="00000007")
    price7, created = MonetaryValue.objects.get_or_create(amount="7.00", currency="GBP", symbol="£")
    transaction7, created = Transaction.objects.get_or_create(payment_type="Visa", payment_method="Debit", price=price7)
    discount7, created = Discount.objects.get_or_create(discount_type="Student", discount_value="0.10", discount_description="Student Railcard")
    concession7, created = Concession.objects.get_or_create(id=record7, mode=bus, operator=zebras, name="Student Railcard", price=price7, discount=discount7, transaction=transaction7, valid_from_date_time=django.utils.timezone.now(), valid_to_date_time=django.utils.timezone.now()+datetime.timedelta(days=728), conditions="Student", customer=customer1)

    # add a purchase to the customer1 account (20 days from now)
    record2, created = RecordID.objects.get_or_create(id="00000002")
    price2, created = MonetaryValue.objects.get_or_create(amount="10.00", currency="GBP", symbol="£")
    transaction2, created = Transaction.objects.get_or_create(payment_type="Visa", payment_method="Debit", price=price2)
    account_balance2, created = MonetaryValue.objects.get_or_create(amount="100.00", currency="GBP", symbol="£")
    ticket2, created = Ticket.objects.get_or_create(reference="GLASGOW-STIRLING", number_usages="0", reference_type="Idk", medium="Idk 2")
    coordinates_from2, created = LatitudeLongitude.objects.get_or_create(latitude=decimal.Decimal(1.5312), longitude=decimal.Decimal(2.5312))
    location_from2, created = Location.objects.get_or_create(lat_long=coordinates_from2, NaPTAN="idk", other="Glasgow", name="Partick")
    coordinates_to2, created = LatitudeLongitude.objects.get_or_create(latitude=decimal.Decimal(3.5312), longitude=decimal.Decimal(4.5312))
    location_to2, created = Location.objects.get_or_create(lat_long=coordinates_to2, NaPTAN="idk", other="Stirling", name="Stirling")
    purchase2, created = Purchase.objects.get_or_create(id=record2, mode=train, operator=zebras, travel_class=first_class, booking_date_time=django.utils.timezone.now(), transaction=transaction2, account_balance=account_balance2, vehicle=vehicle_type, travel_from_date_time=django.utils.timezone.now(), travel_to_date_time=django.utils.timezone.now()+datetime.timedelta(days=20), concession=concession1, ticket=ticket2, location_from=location_from2, location_to=location_to2, customer=customer1)

    # add a second purchase to the customer1 account (30 days ago)
    record8, created = RecordID.objects.get_or_create(id="00000008")
    price8, created = MonetaryValue.objects.get_or_create(amount="12.00", currency="GBP", symbol="£")
    transaction8, created = Transaction.objects.get_or_create(payment_type="Visa", payment_method="Debit", price=price8)
    account_balance8, created = MonetaryValue.objects.get_or_create(amount="100.00", currency="GBP", symbol="£")
    ticket8, created = Ticket.objects.get_or_create(reference="EDINBURGH-DUNDEE", number_usages="0", reference_type="Idk", medium="Idk 2")
    coordinates_from8, created = LatitudeLongitude.objects.get_or_create(latitude=decimal.Decimal(5.5312), longitude=decimal.Decimal(6.5312))
    location_from8, created = Location.objects.get_or_create(lat_long=coordinates_from8, NaPTAN="idk", other="Edinburgh", name="Edinburgh")
    coordinates_to8, created = LatitudeLongitude.objects.get_or_create(latitude=decimal.Decimal(7.5312), longitude=decimal.Decimal(8.5312))
    location_to8, created = Location.objects.get_or_create(lat_long=coordinates_to8, NaPTAN="idk", other="Dundee", name="Dundee")
    purchase8, created = Purchase.objects.get_or_create(id=record8, mode=bus, operator=zebras, travel_class=first_class, booking_date_time=django.utils.timezone.now(), transaction=transaction8, account_balance=account_balance8, vehicle=vehicle_type, travel_from_date_time=django.utils.timezone.now()-datetime.timedelta(days=30), travel_to_date_time=django.utils.timezone.now()-datetime.timedelta(days=1), concession=concession1, ticket=ticket8, location_from=location_from8, location_to=location_to8, customer=customer1)

    # add a third purchase to the customer1 account (10 days ago - 10 days from now)
    record9, created = RecordID.objects.get_or_create(id="00000009")
    price9, created = MonetaryValue.objects.get_or_create(amount="11.00", currency="GBP", symbol="£")
    transaction9, created = Transaction.objects.get_or_create(payment_type="Visa", payment_method="Debit", price=price9)
    account_balance9, created = MonetaryValue.objects.get_or_create(amount="100.00", currency="GBP", symbol="£")
    ticket9, created = Ticket.objects.get_or_create(reference="STIRLING-ST ANDREWS", number_usages="0", reference_type="Idk", medium="Idk 2")
    coordinates_from9, created = LatitudeLongitude.objects.get_or_create(latitude=decimal.Decimal(9.5312), longitude=decimal.Decimal(10.5312))
    location_from9, created = Location.objects.get_or_create(lat_long=coordinates_from9, NaPTAN="idk", name="Arbroath")
    coordinates_to9, created = LatitudeLongitude.objects.get_or_create(latitude=decimal.Decimal(11.5312), longitude=decimal.Decimal(12.5312))
    location_to9, created = Location.objects.get_or_create(lat_long=coordinates_to9, NaPTAN="idk", other="St Andrews", name="St Andrews")
    purchase9, created = Purchase.objects.get_or_create(id=record9, mode=tram, operator=zebras, travel_class=first_class, booking_date_time=django.utils.timezone.now(), transaction=transaction9, account_balance=account_balance9, vehicle=vehicle_type, travel_from_date_time=django.utils.timezone.now()-datetime.timedelta(days=10), travel_to_date_time=django.utils.timezone.now()+datetime.timedelta(days=10), concession=concession1, ticket=ticket9, location_from=location_from9, location_to=location_to9, customer=customer1)

    # add a usage to the customer1 account
    record3, created = RecordID.objects.get_or_create(id="00000003")
    usage_reference3, created = UsageReference.objects.get_or_create(reference="001", reference_type="usage type")

    coordinates_to3, created = LatitudeLongitude.objects.get_or_create(latitude=decimal.Decimal(13.5312), longitude=decimal.Decimal(14.5312))
    location_to3, created = Location.objects.get_or_create(lat_long=coordinates_to3, NaPTAN="idk", other="Glasgow Queen Street", name="Glasgow Queen Street")
    travel_to3, created = UsageFromTo.objects.get_or_create(location=location_to3, date_time=django.utils.timezone.now(), reference="reference usage")

    coordinates_from3, created = LatitudeLongitude.objects.get_or_create(latitude=decimal.Decimal(15.5312), longitude=decimal.Decimal(16.5312))
    location_from3, created = Location.objects.get_or_create(lat_long=coordinates_from3, NaPTAN="idk", other="Gleneagles", name="Gleneagles")
    travel_from3, created = UsageFromTo.objects.get_or_create(location=location_from3, date_time=django.utils.timezone.now()-datetime.timedelta(days=10), reference="reference usage")

    usage3, created = Usage.objects.get_or_create(id=record3, mode=train, operator=zebras, reference=usage_reference3, travel_class=first_class, travel_from=travel_from3, travel_to=travel_to3, purchase_id=purchase2, ticket=ticket2, price=price2, customer=customer1)

    # add a second usage to the customer1 account
    record10, created = RecordID.objects.get_or_create(id="00000010")
    usage_reference10, created = UsageReference.objects.get_or_create(reference="010", reference_type="usage type")

    coordinates_to10, created = LatitudeLongitude.objects.get_or_create(latitude=decimal.Decimal(17.8312), longitude=decimal.Decimal(18.8312))
    location_to10, created = Location.objects.get_or_create(lat_long=coordinates_to10, NaPTAN="idk", other="Edinburgh Haymarket", name="Edinburgh Haymarket")
    travel_to10, created = UsageFromTo.objects.get_or_create(location=location_to10, date_time=django.utils.timezone.now()+datetime.timedelta(days=20), reference="reference usage")

    coordinates_from10, created = LatitudeLongitude.objects.get_or_create(latitude=decimal.Decimal(19.9312), longitude=decimal.Decimal(20.9312))
    location_from10, created = Location.objects.get_or_create(lat_long=coordinates_from10, NaPTAN="idk", other="Pitlochry", name="Pitlochry")
    travel_from10, created = UsageFromTo.objects.get_or_create(location=location_from10, date_time=django.utils.timezone.now()-datetime.timedelta(days=5), reference="reference usage")

    usage10, created = Usage.objects.get_or_create(id=record10, mode=bus, operator=zebras, reference=usage_reference10, travel_class=first_class, travel_from=travel_from10, travel_to=travel_to10, purchase_id=purchase8, ticket=ticket8, price=price8, customer=customer1)
