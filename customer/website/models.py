from django.db import models

# Please refer to https://app.swaggerhub.com/apis/open-transport/customer-account/1.0.1#/
# for details on these models

########### Tomas ##############

class Customer(models.Model):
    pass

class Account(models.Model):
    pass


########## Torrin #############

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
    concession = models.ForeignKey("Concession", on_delete=models.CASCADE)
    restrictions = models.CharField(max_length=500, null=True)
    ticket = models.OneToOneField("Ticket", on_delete=models.CASCADE)
    # Although Purchase has a one-to-many relationship with Location, this is just
    # because Purchase has 2 location fields location_from and location_to.
    # These are still OneToOneFields
    location_from = models.OneToOneField("Location", related_name='requests_created', on_delete=models.CASCADE)
    location_to = models.OneToOneField("Location", on_delete=models.CASCADE)
    reserved_position = models.CharField(max_length=30, null=True)
    # service_request has no relationship with the Service table, it's just a description
    service_request = models.CharField(max_length=500, null=True)
    customer_id = models.ForeignKey("Customer", on_delete=models.CASCADE)

    def __str__(self):
        return "Purchase ID: " + self.id + ", Mode of transport: " + self.mode.short-desc

class Location(models.Model):
    lat_long = models.ForeignKey("LatitudeLongitude", on_delete=models.CASCADE)
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
    id = models.OneToOneField("RecordID", primary_key=True, on_delete=models.CASCADE)
    mode = models.ForeignKey("Mode", on_delete=models.CASCADE)
    reference = models.IntegerField()
    travel_class = models.OneToOneField("TravelClass", on_delete=models.CASCADE)
    travel_from = models.IntegerField()
    travel_to = models.IntegerField()
    purchase_id = models.IntegerField()
    route_via_avoid = models.CharField(max_length=500, null=True)
    ticket_reference = models.OneToOneField("Ticket", on_delete=models.CASCADE)
    pre_paid = models.BooleanField(null=True)
    price = models.OneToOneField("Transaction", on_delete=models.CASCADE)
    customer_id = models.OneToOneField("Account", on_delete=models.CASCADE)
    pass

class UsageReference(models.Model):
    reference = models.CharField(max_length=5)
    reference_type = models.CharField(max_length=10)

    def __str__(self):
        return "Reference: " + reference + ", Reference Type: " + reference_type

class UsageFromTo(models.Model):
    location = models.OneToOneField("Location", on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    reference = models.CharField(max_length=30)

    def __str__(self):
        return "Location: " + location + ", Date-Time: " + date_time + ", Reference: " + reference

class Service(models.Model):
    service_type = models.CharField(max_length=20)
    unit = models.CharField(max_length=10)
    amount = models.IntegerField()
    price = models.OneToOneField("Transaction", on_delete=models.CASCADE)
    usage_id = models.OneToOneField("Usage", on_delete=models.CASCADE)

    def __str__(self):
        return "Service Type: " + service_type + ", Unit: " + unit + ", Amount: " + amount

class TravelClass(models.Model):
    travel_class = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return "Travel Class: " + travel_class

class Ticket(models.Model):
    reference = models.CharField(max_length=30, primary_key=True)
    number_usages = models.CharField(max_length=3)
    reference_type = models.CharField(max_length=30)
    medium = models.CharField(max_length=20, null=True)

    def __str__(self):
        return "Number of Usages: " + number_usages + ", Reference Type: " + reference_type + ", Medium: " + medium



########################################

# The RecordID table stores a list of the IDs of all Purchase, Concession and Usage records
class RecordID(models.Model):
    id = models.CharField(max_length=100, primary_key=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.id

# The Mode table stores the modes of transport this operator provides
class Mode(models.Model):
    id = models.CharField(max_length=10, primary_key=True, on_delete=models.CASCADE)
    short_desc = models.CharField(max_length=50)
    long_desc = models.CharField(max_length=8000, null=True)

    def __str__(self):
        return self.short_desc
    
