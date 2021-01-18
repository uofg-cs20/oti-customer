from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

# Please refer to https://app.swaggerhub.com/apis/open-transport/customer-account/1.0.1#/
# for details on these models

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)

class Account(models.Model):
    operator_id = models.CharField(max_length=50)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    def __str__(self):
        return "Operator ID: " + str(self.operator_id) + ", Customer ID: " + str(self.customer)


class Purchase(models.Model):
    # id is a unique identifier of this Purchase record,
    # which is also stored in the RecordID table
    id = models.OneToOneField("RecordID", primary_key=True, on_delete=models.CASCADE)
    mode = models.ForeignKey("Mode", on_delete=models.CASCADE)
    travel_class = models.ForeignKey("TravelClass", on_delete=models.CASCADE)
    booking_date_time = models.DateTimeField()
    transaction = models.OneToOneField("Transaction", on_delete=models.CASCADE)
    account_balance = models.ForeignKey("MonetaryValue", on_delete=models.CASCADE)
    agent = models.CharField(max_length=100, null=True)
    passenger_number = models.IntegerField(null=True)
    passenger_type = models.CharField(max_length=100, null=True)
    vehicle = models.ForeignKey("Vehicle", on_delete=models.CASCADE)
    route = models.CharField(max_length=500, null=True)
    travel_from_date_time = models.DateTimeField()
    travel_to_date_time = models.DateTimeField()
    conditions = models.CharField(max_length=500, null=True)
    concession = models.ForeignKey("Concession", on_delete=models.CASCADE, null=True)
    restrictions = models.CharField(max_length=500, null=True)
    ticket = models.OneToOneField("Ticket", on_delete=models.CASCADE)
    location_from = models.ForeignKey("Location", related_name="requests_created", on_delete=models.CASCADE)
    location_to = models.ForeignKey("Location", on_delete=models.CASCADE)
    reserved_position = models.CharField(max_length=30, null=True)
    # service_request has no relationship with the Service table, it's just a description
    service_request = models.CharField(max_length=500, null=True)
    customer = models.ForeignKey("Customer", on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)

class Location(models.Model):
    lat_long = models.ForeignKey("LatitudeLongitude", on_delete=models.CASCADE)
    NaPTAN = models.CharField(max_length=10)
    other = models.CharField(max_length=30, null=True)
    other_type = models.CharField(max_length=20, null=True)
    accuracy = models.IntegerField(null=True)
    name = models.CharField(max_length=100, null=True)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return "Lat: " + str(self.lat_long.latitude) + ", Long: " + str(self.lat_long.longitude)

class Vehicle(models.Model):
    included = models.BooleanField(default=True)
    reference = models.CharField(max_length=20)
    vehicle_type = models.CharField(max_length=20)
    conditions = models.CharField(max_length=500, null=True)

    def __str__(self):
        return self.vehicle_type

class LatitudeLongitude(models.Model):
    latitude = models.DecimalField(max_digits=6, decimal_places=4)
    longitude = models.DecimalField(max_digits=7, decimal_places=4)

    def __str__(self):
        latstr = str(self.latitude)
        longstr = str(self.longitude)
        return "Lat: " + latstr + ", Long: " + longstr

class MonetaryValue(models.Model):
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    currency = models.CharField(max_length=3)
    symbol = models.CharField(max_length=1, null=True)

    def __str__(self):
        if self.symbol:
            return self.symbol + str(self.amount)
        else:
            return str(self.amount) + " " + self.currency

class Transaction(models.Model):
    date_time = models.DateTimeField(auto_now_add=True)
    payment_type = models.CharField(max_length=30)
    payment_method = models.CharField(max_length=30)
    price = models.ForeignKey(MonetaryValue, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)

class Discount(models.Model):
    discount_type = models.CharField(max_length=50)
    discount_value = models.DecimalField(max_digits=6, decimal_places=2)
    discount_description = models.CharField(max_length=100)

    def __str__(self):
        return str(self.discount_value)

class Concession(models.Model):
    id = models.OneToOneField("RecordID", primary_key=True, on_delete=models.CASCADE)
    mode = models.ForeignKey("Mode", on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    price = models.ForeignKey("MonetaryValue", on_delete=models.CASCADE)
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    valid_from_date_time = models.DateField()
    valid_to_date_time = models.DateField()
    conditions = models.CharField(max_length=500)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    def __str__(self):
        return "Concession Id: " + str(self.id) + ", Concession name: " + str(self.name)


class Usage(models.Model):
    id = models.OneToOneField("RecordID", primary_key=True, related_name="recordid", on_delete=models.CASCADE)
    mode = models.ForeignKey("Mode", on_delete=models.CASCADE)
    reference = models.ForeignKey("UsageReference", on_delete=models.CASCADE)
    travel_class = models.ForeignKey("TravelClass", on_delete=models.CASCADE)
    travel_from = models.ForeignKey("UsageFromTo", related_name="requests_created", on_delete=models.CASCADE)
    travel_to = models.ForeignKey("UsageFromTo", on_delete=models.CASCADE)
    purchase_id = models.ForeignKey("Purchase", on_delete=models.CASCADE)
    route_via_avoid = models.CharField(max_length=500, null=True)
    ticket_reference = models.ForeignKey("Ticket", on_delete=models.CASCADE)
    pre_paid = models.BooleanField(null=True)
    price = models.ForeignKey("MonetaryValue", on_delete=models.CASCADE)
    customer = models.ForeignKey("Customer", on_delete=models.CASCADE)

    def __str__(self):
        return "Usage ID: " + str(self.id) + ", Customer ID: " + str(self.customer)   

class UsageReference(models.Model):
    reference = models.CharField(max_length=5)
    reference_type = models.CharField(max_length=10)

    def __str__(self):
        return self.reference

class UsageFromTo(models.Model):
    location = models.ForeignKey("Location", on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    reference = models.CharField(max_length=30)

    def __str__(self):
        return "Location: " + str(self.location)

class Service(models.Model):
    service_type = models.CharField(max_length=20)
    unit = models.CharField(max_length=10)
    amount = models.IntegerField()
    price = models.ForeignKey("MonetaryValue", on_delete=models.CASCADE)
    usage_id = models.ForeignKey("Usage", on_delete=models.CASCADE)

    def __str__(self):
        return "Service Type: " + self.service_type + ", Unit: " + self.unit + ", Amount: " + self.amount

class TravelClass(models.Model):
    travel_class = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.travel_class

class Ticket(models.Model):
    reference = models.CharField(max_length=30, primary_key=True)
    number_usages = models.CharField(max_length=3)
    reference_type = models.CharField(max_length=30)
    medium = models.CharField(max_length=20, null=True)

    def __str__(self):
        return self.reference


# The RecordID table stores a list of the IDs of all Purchase, Concession and Usage records
class RecordID(models.Model):
    id = models.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return self.id

# The Mode table stores the modes of transport this operator provides
class Mode(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    short_desc = models.CharField(max_length=50)
    long_desc = models.CharField(max_length=8000, null=True)

    def __str__(self):
        return self.short_desc
    
