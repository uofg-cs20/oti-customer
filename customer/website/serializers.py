from .models import Purchase, Concession, Usage, Mode, MonetaryValue, Discount, Transaction, Customer
from rest_framework import serializers

"""
TO-DO:
Define serializer classes for all models relating to
Purchase, Concession & Usage. The order they are defined
is important - a serializer cannot reference another
serializer that is not yet defined. Each serializer
class should overwrite fields which are foreign keys
with an instance of that respective serializer.
"""

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
    class Meta:
        model = Customer
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
        
    class Meta:
        model = Purchase
        fields = '__all__'

class UsageSerializer(serializers.ModelSerializer):
    purchase_id = PurchaseSerializer()
        
    class Meta:
        model = Usage
        fields = '__all__'

