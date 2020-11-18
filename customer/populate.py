import os, random
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'customer.settings')

import django
django.setup()

import decimal 

from django.contrib.auth.models import User
from website.models import *
from django.utils.timezone import make_aware

def populate():

    # delete data f the database is already populated
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



    d = decimal.Decimal(1.5312) 
    d2 = decimal.Decimal(2.3245)
    d3 = decimal.Decimal(3.5312) 
    d4 = decimal.Decimal(4.3245)
    d5 = decimal.Decimal(5.5312) 
    d6 = decimal.Decimal(6.3245)
    d7 = decimal.Decimal(7.5312) 
    d8 = decimal.Decimal(8.3245)

    # superuser account - use this to log into the django admin page
    dev = User.objects.create_user(username='dev', password='1234', is_superuser=True, is_staff=True, email="dev@project.com", first_name='dev')

    # create a customer
    user1 = User.objects.create_user(username='tomas', password='1234', email='tomas@scotrail.co.uk.', first_name='Tomas Mikus')
    customer1, created = Customer.objects.get_or_create(user=user1)
    account1, created = Account.objects.get_or_create(customer=customer1, operator_id="Scotrail")

    # add a concession purchase to a customer account
    record, created = RecordID.objects.get_or_create(id="00000001")
    price, created = MonetaryValue.objects.get_or_create(amount="30.00", currency="GBP")
    transaction, created = Transaction.objects.get_or_create(payment_type="Visa", payment_method="Debit", price=price)
    discount, created = Discount.objects.get_or_create(discount_type="Young person", discount_value="0.20", discount_description="16-25 Railcard")
    concession, created = Concession.objects.get_or_create(id=record, name="16-25 Railcard", price="30.00", discount=discount, transaction=transaction, valid_from_date_time="2020-01-01", valid_to_date_time="2022-01-01", conditions="Below 25", customer=customer1)

    record2, created = RecordID.objects.get_or_create(id="00000002")
    train, created = Mode.objects.get_or_create(id="train", short_desc="Train")
    first_class, created = TravelClass.objects.get_or_create(travel_class="First Class")
    price2, created = MonetaryValue.objects.get_or_create(amount="10.00", currency="GBP")
    transaction2, created = Transaction.objects.get_or_create(payment_type="Visa", payment_method="Debit", price=price2)
    account_balance1, created = MonetaryValue.objects.get_or_create(amount="100.00", currency="GBP")
    vehicle_type, created = Vehicle.objects.get_or_create(reference="train 3001", vehicle_type="train")
    ticket1, created = Ticket.objects.get_or_create(reference="GLA-STL 102413134", number_usages="0", reference_type="Idk", medium="Idk 2")
    coordinates_from, created = LatitudeLongitude.objects.get_or_create(latitude=d, longitude=d2)
    location_from, created = Location.objects.get_or_create(lat_long=coordinates_from, NaPTAN="idk")
    coordinates_to, created = LatitudeLongitude.objects.get_or_create(latitude=d3, longitude=d4)
    location_to, created = Location.objects.get_or_create(lat_long=coordinates_to, NaPTAN="idk")
    purchase1, created = Purchase.objects.get_or_create(id=record2, mode=train, travel_class=first_class, booking_date_time=django.utils.timezone.now(), transaction=transaction2, account_balance=account_balance1, vehicle=vehicle_type, travel_from_date_time=django.utils.timezone.now(), travel_to_date_time=django.utils.timezone.now(), concession=concession, ticket=ticket1, location_from=location_from, location_to=location_to, customer=customer1)



    record3, created = RecordID.objects.get_or_create(id="00000003")
    usage_reference1, created = UsageReference.objects.get_or_create(reference="001", reference_type="usage type")

    coordinates_to2, created = LatitudeLongitude.objects.get_or_create(latitude=d5, longitude=d6)
    location_to2, created = Location.objects.get_or_create(lat_long=coordinates_to2, NaPTAN="idk")
    travel_to2, created = UsageFromTo.objects.get_or_create(location=location_to2, date_time=django.utils.timezone.now(), reference="reference usage")

    coordinates_from2, created = LatitudeLongitude.objects.get_or_create(latitude=d7, longitude=d8)
    location_from2, created = Location.objects.get_or_create(lat_long=coordinates_from2, NaPTAN="idk")
    travel_from2, created = UsageFromTo.objects.get_or_create(location=location_from2, date_time=django.utils.timezone.now(), reference="reference usage")

    usage, created = Usage.objects.get_or_create(id=record3, mode=train, reference=usage_reference1, travel_class=first_class, travel_from=travel_from2, travel_to=travel_to2, purchase_id=purchase1, ticket_reference=ticket1, price=price2, customer=customer1)

if __name__ == '__main__':
    print('Starting population script...', end="")
    populate()
    print('DONE')