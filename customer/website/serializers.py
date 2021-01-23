from .models import Purchase, Concession, Usage, Mode, MonetaryValue, Discount, Transaction, Service
from .models import TravelClass, UsageFromTo, Location, LatitudeLongitude, Vehicle, UsageReference, Ticket, Operator
from rest_framework import serializers


class ModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mode
        fields = '__all__'
        
class OperatorSerializer(serializers.ModelSerializer):
    modes = ModeSerializer(many=True)
    
    class Meta:
        model = Operator
        fields = ['id', 'name', 'modes', 'homepage', 'api_url', 'default_language', 'phone', 'email']

class MonetaryValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonetaryValue
        fields = ['amount', 'currency']

class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = ['discount_type', 'discount_value', 'discount_description']

class TransactionSerializer(serializers.ModelSerializer):
    price = MonetaryValueSerializer()

    class Meta:
        model = Transaction
        fields = ['date_time', 'reference', 'payment_type', 'payment_method', 'price']

class LatitudeLongitudeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LatitudeLongitude
        fields = ['latitude', 'longitude']

class LocationSerializer(serializers.ModelSerializer):
    lat_long = LatitudeLongitudeSerializer()

    class Meta:
        model = Location
        fields = ['lat_long', 'NaPTAN', 'other', 'other_type', 'accuracy']

class UsageFromToSerializer(serializers.ModelSerializer):
    location = LocationSerializer()

    class Meta:
        model = UsageFromTo
        fields = ['location', 'date_time', 'reference']

class UsageReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsageReference
        fields = ['reference', 'reference_type']

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['included', 'reference', 'vehicle_type', 'conditions']

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['number_usages', 'reference', 'reference_type', 'medium']
        
class ServiceSerializer(serializers.ModelSerializer):
    price = MonetaryValueSerializer()
    
    class Meta:
        model = Service
        fields = ['service_type', 'unit', 'amount', 'price']

class ConcessionSerializer(serializers.ModelSerializer):
    mode = ModeSerializer()
    operator = OperatorSerializer()
    price = MonetaryValueSerializer()
    discount = DiscountSerializer()
    transaction = TransactionSerializer()

    class Meta:
        model = Concession
        fields = ['id', 'mode', 'operator', 'name', 'price', 'discount', 'transaction', 'valid_from_date_time', 'valid_to_date_time', 'conditions']

class PurchaseSerializer(serializers.ModelSerializer):
    mode = ModeSerializer()
    operator = OperatorSerializer()
    concession = serializers.StringRelatedField()
    account_balance = MonetaryValueSerializer()
    vehicle = VehicleSerializer()
    location_from = LocationSerializer()
    location_to = LocationSerializer()
    transaction = TransactionSerializer()
    ticket = TicketSerializer()

    class Meta:
        model = Purchase
        fields = ['id', 'mode', 'operator', 'travel_class', 'booking_date_time', 'transaction', 'account_balance', 'agent', 'passenger_number', 'passenger_type', 'vehicle', 'route', 'travel_from_date_time', 'travel_to_date_time', 'conditions', 'concession', 'restrictions', 'ticket', 'location_from', 'location_to', 'reserved_position', 'service_request']

class UsageSerializer(serializers.ModelSerializer):
    mode = ModeSerializer()
    operator = OperatorSerializer()
    reference = UsageReferenceSerializer()
    travel_from = UsageFromToSerializer()
    travel_to = UsageFromToSerializer()
    ticket = TicketSerializer()
    price = MonetaryValueSerializer()
    services = ServiceSerializer(many=True)
    
    class Meta:
        model = Usage
        fields = ['id', 'mode', 'operator', 'reference', 'travel_class', 'travel_from', 'travel_to', 'purchase_id', 'route_via_avoid', 'ticket', 'pre_paid', 'price', 'services']

