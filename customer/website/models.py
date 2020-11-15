from django.db import models


########### Tomas ##############

class Customer(models.Model):
    pass

class Account(models.Model):
    pass


########## Torrin #############

class Purchase(models.Model):
    # id may change if our interpretation of RecordID was wrong
    id = models.OneToOneField("RecordID", primary_key=True)
    travel_class = models.OneToOneField("TravelClass")
    booking_date_time = models.DateTimeField()
    transaction = models.OneToOneField("Transaction")
    account_balance = models.OneToOneField("MonetaryValue")
    agent = models.CharField(max_length=100, null=True)
    passenger_number = models.IntegerField(null=True)
    passenger_type = models.CharField(max_length=100, null=True)
    vehicle = models.OneToOneField("Vehicle")
    route = models.CharField(max_length=500, null=True)
    travel_from_date_time = models.DateTimeField()
    travel_to_date_time = models.DateTimeField()
    conditions = models.CharField(max_length=500, null=True)
    concession = models.OneToOneField("Concession")
    restrictions = models.CharField(max_length=500, null=True)
    ticket = models.OneToOneField("Ticket")
    # Although Purchase has a one-to-many relationship with Location, this is just
    # because Purchase has 2 location fields location_from and location_to.
    # These are still OneToOneFields
    location_from = models.OneToOneField("Location")
    location_to = models.OneToOneField("Location")
    reserved_position = models.CharField(max_length=30, null=True)
    # service_request has no relationship with the Service table, it's just a description
    service_request = models.CharField(max_length=500, null=True)
    customer_id = models.ForeignKey("Customer")

    def __str__(self):
        return "Purchase ID: " + self.id

class Location(models.Model):
    lat_long = models.ForeignKey("LatitudeLongitude")
    NaPTAN = models.CharField(max_length=10)
    other = models.CharField(max_length=30, null=True)
    other_type = models.CharField(max_length=20, null=True)
    accuracy = models.IntegerField(null=True)

    def __str__(self):
        return "Lat: " + str(self.lat_long.latitude) + ", Long: " + str(self.lat_long.longitude) + ", NaPTAN: " + self.NaPTAN

class Vehicle(models.Model):
    included = models.BooleanField(default=True)
    reference = models.CharField(max_length=20)
    vehicle_type = models.CharField(max_length=20)
    conditions = models.CharField(max_length=500, null=True)

    def __str__(self):
        return "Type: " + self.vehicle_type + ", Reference: " + self.reference

class LatitudeLongitude(models.Model):
    latitude = models.DecimalField(max_digits=6, decimal_places=4)
    longitude = models.DecimalField(max_digits=7, decimal_places=4)

    def __str__(self):
        latstr = str(self.latitude)
        longstr = str(self.longitude)
        return "Lat: " + latstr + ", Long: " + longstr


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
