from .models import Purchase, Concession, Usage
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

class ConcessionSerializer(serializers.ModelSerializer):
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

