from dataclasses import field
from .models         import Payment, PaymentTransaction
from users.models    import User

from rest_framework import serializers, validators

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields =[
            'id',
            'paid_price',
            'used_point',
            'payment_method',
            'product_type',
            'is_refunded'
        ]

class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        field = [
            'order_id',
            'transaction_id',
            'amount',
            'transaction_status',
            'type'
        ]