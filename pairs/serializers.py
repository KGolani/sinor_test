from dataclasses import field
from rest_framework    import serializers

from .models           import Location, Wishlist, UserInterest
from users.models      import User

class LocationSerializer(serializers.ModelSerializer):

    class Meta:
        model            = Location
        fields           = ('longtitude', 'latitude', 'max_distance', 'user')
        read_only_fields = ('id',)

class WishListSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Wishlist
        fields = ('id','liked_user','user')


class UserSerializer(serializers.ModelSerializer):
    location_set = LocationSerializer(many=True, read_only=True)
    to_user_set  = WishListSerializer(many=True, read_only=True)

    class Meta:
        model  = User
        fields = ['id',
                  'phone_number',
                  'name',
                  'gender',
                  'birth_year',
                  'location_set',
                  'to_user_set'
                ]

class FilterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'sendbird_id',
            'phone_number',
            'name',
            'gender',
            'birth_year',
            'birth_date',
            'point',
            'reported_count',
            'is_deleted'
        ]

class InterestTestSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserInterest
        fields = [
            'id',
            'user_id',
            'interest_id',
            'sequence'
        ]