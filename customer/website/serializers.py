from .models import *
from rest_framework import serializers


# Given a list of field names with a given delimiter, returns a list of
# field names with the specified character as a delimiter, along with a
# dictionary of source fields
def formatFields(fields, current_delimiter='_', new_delimiter='-'):
    formatted_fields = []
    source_fields = {}
    for f in fields:
        formatted_str = f
        if current_delimiter in f:
            formatted_str = f.replace(current_delimiter, new_delimiter)
            source_fields[formatted_str] = {'source': f}
        formatted_fields.append(formatted_str)
    return formatted_fields, source_fields


class ModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mode
        fields = ['id', 'short_desc', 'long_desc']
        fields, extra_kwargs = formatFields(fields)
        
class OperatorSerializer(serializers.ModelSerializer):
    modes = ModeSerializer(many=True)
    
    class Meta:
        model = Operator
        fields = ['id', 'name', 'modes', 'homepage', 'api_url', 'default_language', 'phone', 'email']
        fields, extra_kwargs = formatFields(fields)

class MonetaryValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonetaryValue
        fields = ['amount', 'currency']
        fields, extra_kwargs = formatFields(fields)

class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = ['discount_type', 'discount_value', 'discount_description']
        fields, extra_kwargs = formatFields(fields)

class TransactionSerializer(serializers.ModelSerializer):
    price = MonetaryValueSerializer()

    class Meta:
        model = Transaction
        fields = ['date_time', 'reference', 'payment_type', 'payment_method', 'price']
        fields, extra_kwargs = formatFields(fields)

class LatitudeLongitudeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LatitudeLongitude
        fields = ['latitude', 'longitude']
        fields, extra_kwargs = formatFields(fields)

class LocationSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        self.fields["lat-long"] = LatitudeLongitudeSerializer(source="lat_long")
        super().__init__(*args, **kwargs)

    class Meta:
        model = Location
        fields = ['lat_long', 'NaPTAN', 'other', 'other_type', 'accuracy']
        fields, extra_kwargs = formatFields(fields)

class UsageFromToSerializer(serializers.ModelSerializer):
    location = LocationSerializer()

    class Meta:
        model = UsageFromTo
        fields = ['location', 'date_time', 'reference']
        fields, extra_kwargs = formatFields(fields)

class UsageReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsageReference
        fields = ['reference', 'reference_type']
        fields, extra_kwargs = formatFields(fields)

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['included', 'reference', 'vehicle_type', 'conditions']
        fields, extra_kwargs = formatFields(fields)

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['number_usages', 'reference', 'reference_type', 'medium']
        fields, extra_kwargs = formatFields(fields)
        
class ServiceSerializer(serializers.ModelSerializer):
    price = MonetaryValueSerializer()
    
    class Meta:
        model = Service
        fields = ['service_type', 'unit', 'amount', 'price']
        fields, extra_kwargs = formatFields(fields)

class ConcessionSerializer(serializers.ModelSerializer):
    mode = ModeSerializer()
    operator = OperatorSerializer()
    price = MonetaryValueSerializer()
    discount = DiscountSerializer()
    transaction = TransactionSerializer()

    class Meta:
        model = Concession
        fields = ['id', 'mode', 'operator', 'name', 'price', 'discount', 'transaction', 'valid_from_date_time', 'valid_to_date_time', 'conditions']
        fields, extra_kwargs = formatFields(fields)

class PurchaseSerializer(serializers.ModelSerializer):
    mode = ModeSerializer()
    operator = OperatorSerializer()
    concession = serializers.StringRelatedField()
    vehicle = VehicleSerializer()
    transaction = TransactionSerializer()
    ticket = TicketSerializer()
    
    def __init__(self, *args, **kwargs):
        self.fields["account-balance"] = MonetaryValueSerializer(source="account_balance")
        self.fields["location-from"] = LocationSerializer(source="location_from")
        self.fields["location-to"] = LocationSerializer(source="location_to")
        super().__init__(*args, **kwargs)

    class Meta:
        model = Purchase
        fields = ['id', 'mode', 'operator', 'travel_class', 'booking_date_time', 'transaction', 'account_balance', 'agent', 'passenger_number', 'passenger_type', 'vehicle', 'route', 'travel_from_date_time', 'travel_to_date_time', 'conditions', 'concession', 'restrictions', 'ticket', 'location_from', 'location_to', 'reserved_position', 'service_request']
        fields, extra_kwargs = formatFields(fields)

class UsageSerializer(serializers.ModelSerializer):
    mode = ModeSerializer()
    operator = OperatorSerializer()
    reference = UsageReferenceSerializer()
    ticket = TicketSerializer()
    price = MonetaryValueSerializer()
    services = ServiceSerializer(many=True)
    
    def __init__(self, *args, **kwargs):
        self.fields["travel-from"] = UsageFromToSerializer(source="travel_from")
        self.fields["travel-to"] = UsageFromToSerializer(source="travel_to")
        super().__init__(*args, **kwargs)
    
    class Meta:
        model = Usage
        fields = ['id', 'mode', 'operator', 'reference', 'travel_class', 'travel_from', 'travel_to', 'purchase_id', 'route_via_avoid', 'ticket', 'pre_paid', 'price', 'services']
        fields, extra_kwargs = formatFields(fields)


