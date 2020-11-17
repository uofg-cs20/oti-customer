import os, random
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'customer.settings')

import django
django.setup()

from datetime import date
from django.contrib.auth.models import User
from website.models import *

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

    # superuser account - use this to log into the django admin page
    dev = User.objects.create_user(username='dev', password='1234', is_superuser=True, is_staff=True, email="dev@project.com", first_name='dev')

    # create a customer
    user1 = User.objects.create_user(username='tomas', password='1234', email='tomas@scotrail.co.uk.', first_name='Tomas Mikus')
    customer1, created = Customer.objects.get_or_create(user=user1)
    account1, created = Account.objects.get_or_create(customer=customer1, operator_id="Scotrail")

    # add a concession purchase to a customer account
    price, created = MonetaryValue.objects.get_or_create(amount="30.00", currency="GBP")
    transaction, created = Transaction.objects.get_or_create(payment_type="Visa", payment_method="Debit", price=price)
    discount, created = Discount.objects.get_or_create(discount_type="Young person", discount_value="0.20", discount_description="16-25 Railcard")
    concession, created = Concession.objects.get_or_create(name="16-25 Railcard", price="30.00", discount=discount, transaction=transaction, valid_from_date_time="2020-01-01", valid_to_date_time="2022-01-01", conditions="Below 25", customer=customer1)

if __name__ == '__main__':
    print('Starting population script...', end="")
    populate()
    print('DONE')