from dataclasses import fields
from .models         import Product, Announcement, Event
from payments.models import Coupon
from users.models   import User

from rest_framework import serializers, validators

class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = "__all__"

class PointSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields =["id","point"]

class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = "__all__"


class EventSerializer(serializers.ModelSerializer):
    image_url = serializers.ImageField(use_url=True)

    class Meta:
        model = Event
        fields = "__all__"