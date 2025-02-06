from rest_framework import serializers
from .models import Listing
from .models import Booking
from .models import Payment

class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'booking', 'transaction_id', 'amount', 'status', 'created_at', 'updated_at']
        read_only_fields = ['transaction_id', 'status', 'created_at', 'updated_at']