from .models import Purchase, Concession, Usage, Mode, MonetaryValue, Discount, Transaction, Customer
from .models import TravelClass, UsageFromTo, Location, LatitudeLongitude, Vehicle, UsageReference, Ticket
from rest_framework import serializers
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Returning the user's password may not be very secure, but it can be used
        # for account verification during testing
        fields = ['id', 'email', 'username', 'password']

class ModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mode
        fields = '__all__'

class MonetaryValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonetaryValue
        fields = '__all__'

class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    price = MonetaryValueSerializer()

    class Meta:
        model = Transaction
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Customer
        fields = '__all__'

class TravelClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelClass
        fields = '__all__'

class LatitudeLongitudeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LatitudeLongitude
        fields = '__all__'

class LocationSerializer(serializers.ModelSerializer):
    lat_long = LatitudeLongitudeSerializer()

    class Meta:
        model = Location
        fields = '__all__'

class UsageFromToSerializer(serializers.ModelSerializer):
    location = LocationSerializer()

    class Meta:
        model = UsageFromTo
        fields = '__all__'

class UsageReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsageReference
        fields = '__all__'

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'

class ConcessionSerializer(serializers.ModelSerializer):
    mode = ModeSerializer()
    price = MonetaryValueSerializer()
    discount = DiscountSerializer()
    transaction = TransactionSerializer()
    customer = CustomerSerializer()

    class Meta:
        model = Concession
        fields = '__all__'

class PurchaseSerializer(serializers.ModelSerializer):
    concession = ConcessionSerializer()
    mode = ModeSerializer()
    travel_class = TravelClassSerializer()
    account_balance = MonetaryValueSerializer()
    vehicle = VehicleSerializer()
    location_from = LocationSerializer()
    location_to = LocationSerializer()
    customer = CustomerSerializer()

    class Meta:
        model = Purchase
        fields = '__all__'

class UsageSerializer(serializers.ModelSerializer):
    purchase_id = PurchaseSerializer()
    mode = ModeSerializer()
    reference = UsageReferenceSerializer()
    travel_class = TravelClassSerializer()
    travel_from = UsageFromToSerializer()
    travel_to = UsageFromToSerializer()
    ticket_reference = TicketSerializer()
    price = MonetaryValueSerializer()
    customer = CustomerSerializer()
    
    class Meta:
        model = Usage
        fields = '__all__'

