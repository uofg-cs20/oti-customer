from django.db import models


########### Tomas ##############

class Customer(models.Model):
    pass

class Account(models.Model):
    pass


########## Torrin #############

class Purchase(models.Model):
    id = models.OneToOneField("RecordID") # This may change if our interpretation of RecordID was wrong
    travel_class = models.OneToOneField("TravelClass")
    booking_date_time = models.DateTimeField()
    transaction = models.OneToOneField("Transaction")
    account_balance = models.OneToOneField("MonetaryValue")
    agent = models.CharField(max_length=100)
    passenger_number = models.IntegerField()
    passenger_type = models.CharField(max_length=100)
    vehicle = models.OneToOneField("Vehicle")
    route = models.CharField(max_length=500)
    travel_from_date_time = models.DateTimeField()
    travel_to_date_time = models.DateTimeField()
    conditions = models.CharField(max_length=500)
    concession = models.OneToOneField("Concession")
    restrictions = models.CharField(max_length=500)
    ticket = models.OneToOneField("Ticket")
    # Although Purchase has a one-to-many relationship with Location, this is just
    # because Purchase has 2 location fields location_from and location_to.
    # These are still OneToOneFields
    location_from = models.OneToOneField("Location")
    location_to = models.OneToOneField("Location")
    reserved_position = models.CharField(max_length=30)
    service_request = models.CharField(max_length=500)
    customer_id = models.ForeignKey("Customer")

class Location(models.Model):
    pass

class Vehicle(models.Model):
    pass

class LatitudeLongitude(models.Model):
    pass


############ Tomas #############

class Concession(models.Model):
    pass

class Discount(models.Model):
    pass

class Transaction(models.Model):
    pass

class MonetaryValue(models.Model):
    pass


############## Kameron ##############

class Usage(models.Model):
    pass

class UsageReference(models.Model):
    pass

class UsageFromTo(models.Model):
    pass

class Service(models.Model):
    pass

class TravelClass(models.Model):
    pass

class Ticket(models.Model):
    pass


########################################

class RecordID(models.Model):
    pass
