import os, random
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'customer.settings')

import django
django.setup()

import decimal 
import datetime

from django.contrib.auth.models import User
from website.models import *
from django.utils.timezone import make_aware

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
    first_class, created = TravelClass.objects.get_or_create(travel_class="First Class")
    vehicle_type, created = Vehicle.objects.get_or_create(reference="train 3001", vehicle_type="train")

    # create customer 1
    user1 = User.objects.create_user(username='tomas', password='1234', email='tomas@scotrail.co.uk.', first_name='Tomas')
    customer1, created = Customer.objects.get_or_create(user=user1)
    account1, created = Account.objects.get_or_create(customer=customer1, operator_id="Scotrail")

    # add a concession purchase to the customer1 account
    record1, created = RecordID.objects.get_or_create(id="00000001")
    price1, created = MonetaryValue.objects.get_or_create(amount="30.00", currency="GBP")
    transaction1, created = Transaction.objects.get_or_create(payment_type="Visa", payment_method="Debit", price=price1)
    discount1, created = Discount.objects.get_or_create(discount_type="Young person", discount_value="0.20", discount_description="16-25 Railcard")
    concession1, created = Concession.objects.get_or_create(id=record1, mode=train, name="16-25 Railcard", price="30.00", discount=discount1, transaction=transaction1, valid_from_date_time=django.utils.timezone.now(), valid_to_date_time=django.utils.timezone.now()+datetime.timedelta(days=728), conditions="Below 25", customer=customer1)

    # add a purchase to the customer1 account
    record2, created = RecordID.objects.get_or_create(id="00000002")
    price2, created = MonetaryValue.objects.get_or_create(amount="10.00", currency="GBP")
    transaction2, created = Transaction.objects.get_or_create(payment_type="Visa", payment_method="Debit", price=price2)
    account_balance2, created = MonetaryValue.objects.get_or_create(amount="100.00", currency="GBP")
    ticket2, created = Ticket.objects.get_or_create(reference="GLA-STL 102413134", number_usages="0", reference_type="Idk", medium="Idk 2")
    coordinates_from2, created = LatitudeLongitude.objects.get_or_create(latitude=decimal.Decimal(1.5312), longitude=decimal.Decimal(2.5312))
    location_from2, created = Location.objects.get_or_create(lat_long=coordinates_from2, NaPTAN="idk")
    coordinates_to2, created = LatitudeLongitude.objects.get_or_create(latitude=decimal.Decimal(3.5312), longitude=decimal.Decimal(4.5312))
    location_to2, created = Location.objects.get_or_create(lat_long=coordinates_to2, NaPTAN="idk")
    purchase2, created = Purchase.objects.get_or_create(id=record2, mode=train, travel_class=first_class, booking_date_time=django.utils.timezone.now(), transaction=transaction2, account_balance=account_balance2, vehicle=vehicle_type, travel_from_date_time=django.utils.timezone.now(), travel_to_date_time=django.utils.timezone.now()+datetime.timedelta(days=30), concession=concession1, ticket=ticket2, location_from=location_from2, location_to=location_to2, customer=customer1)

    # add a usage to the customer1 account
    record3, created = RecordID.objects.get_or_create(id="00000003")
    usage_reference3, created = UsageReference.objects.get_or_create(reference="001", reference_type="usage type")

    coordinates_to3, created = LatitudeLongitude.objects.get_or_create(latitude=decimal.Decimal(5.5312), longitude=decimal.Decimal(6.5312))
    location_to3, created = Location.objects.get_or_create(lat_long=coordinates_to3, NaPTAN="idk")
    travel_to3, created = UsageFromTo.objects.get_or_create(location=location_to3, date_time=django.utils.timezone.now(), reference="reference usage")

    coordinates_from3, created = LatitudeLongitude.objects.get_or_create(latitude=decimal.Decimal(7.5312), longitude=decimal.Decimal(8.5312))
    location_from3, created = Location.objects.get_or_create(lat_long=coordinates_from3, NaPTAN="idk")
    travel_from3, created = UsageFromTo.objects.get_or_create(location=location_from3, date_time=django.utils.timezone.now()-datetime.timedelta(days=10), reference="reference usage")

    usage3, created = Usage.objects.get_or_create(id=record3, mode=train, reference=usage_reference3, travel_class=first_class, travel_from=travel_from3, travel_to=travel_to3, purchase_id=purchase2, ticket_reference=ticket2, price=price2, customer=customer1)

    # create customer 2
    user2 = User.objects.create_user(username='torrin', password='1234', email='torrin@scotrail.co.uk.', first_name='Torrin')
    customer2, created = Customer.objects.get_or_create(user=user2)
    account2, created = Account.objects.get_or_create(customer=customer2, operator_id="Scotrail")

    # add a concession purchase to the customer2 account
    record6, created = RecordID.objects.get_or_create(id="00000006")
    price6, created = MonetaryValue.objects.get_or_create(amount="10.00", currency="GBP")
    transaction6, created = Transaction.objects.get_or_create(payment_type="Visa", payment_method="Debit", price=price6)
    discount6, created = Discount.objects.get_or_create(discount_type="Senior Traveller", discount_value="0.50", discount_description="Over 60 yrs")
    concession6, created = Concession.objects.get_or_create(id=record6, mode=train, name="Senior Traveller", price="10.00", discount=discount6, transaction=transaction6, valid_from_date_time=django.utils.timezone.now(), valid_to_date_time=django.utils.timezone.now()+datetime.timedelta(days=364), conditions="Over 60", customer=customer2)

    # add a purchase to the customer2 account
    record4, created = RecordID.objects.get_or_create(id="00000004")
    price4, created = MonetaryValue.objects.get_or_create(amount="15.00", currency="GBP")
    transaction4, created = Transaction.objects.get_or_create(payment_type="Visa", payment_method="Debit", price=price4)
    account_balance4, created = MonetaryValue.objects.get_or_create(amount="50.00", currency="GBP")
    ticket4, created = Ticket.objects.get_or_create(reference="GLA-EDB 102413134", number_usages="0", reference_type="Idk", medium="Idk 2")
    coordinates_from4, created = LatitudeLongitude.objects.get_or_create(latitude=decimal.Decimal(1.5312), longitude=decimal.Decimal(2.5312))
    location_from4, created = Location.objects.get_or_create(lat_long=coordinates_from4, NaPTAN="idk")
    coordinates_to4, created = LatitudeLongitude.objects.get_or_create(latitude=decimal.Decimal(3.5312), longitude=decimal.Decimal(4.5312))
    location_to4, created = Location.objects.get_or_create(lat_long=coordinates_to4, NaPTAN="idk")
    purchase4, created = Purchase.objects.get_or_create(id=record4, mode=train, travel_class=first_class, booking_date_time=django.utils.timezone.now(), transaction=transaction4, account_balance=account_balance4, vehicle=vehicle_type, travel_from_date_time=django.utils.timezone.now(), travel_to_date_time=django.utils.timezone.now()+datetime.timedelta(days=30), concession=concession6, ticket=ticket4, location_from=location_from4, location_to=location_to4, customer=customer2)

    # add a usage to the customer2 account
    record5, created = RecordID.objects.get_or_create(id="00000005")
    usage_reference5, created = UsageReference.objects.get_or_create(reference="002", reference_type="usage type")

    coordinates_to5, created = LatitudeLongitude.objects.get_or_create(latitude=decimal.Decimal(5.5312), longitude=decimal.Decimal(6.5312))
    location_to5, created = Location.objects.get_or_create(lat_long=coordinates_to5, NaPTAN="idk")
    travel_to5, created = UsageFromTo.objects.get_or_create(location=location_to5, date_time=django.utils.timezone.now(), reference="reference usage")

    coordinates_from5, created = LatitudeLongitude.objects.get_or_create(latitude=decimal.Decimal(7.5312), longitude=decimal.Decimal(8.5312))
    location_from5, created = Location.objects.get_or_create(lat_long=coordinates_from5, NaPTAN="idk")
    travel_from5, created = UsageFromTo.objects.get_or_create(location=location_from5, date_time=django.utils.timezone.now()-datetime.timedelta(days=10), reference="reference usage")

    usage5, created = Usage.objects.get_or_create(id=record5, mode=train, reference=usage_reference5, travel_class=first_class, travel_from=travel_from5, travel_to=travel_to5, purchase_id=purchase4, ticket_reference=ticket4, price=price4, customer=customer2)

if __name__ == '__main__':
    print('Starting population script...', end="")
    populate()
    print('DONE')