from rest_framework import serializers, validators

from users.models import User, AuthenticationNumber, UserProfile, UserImage
from pairs.models import UserInterest, Interest


class UserImageSerializer(serializers.ModelSerializer):
    class Meta:
        model            = UserImage
        fields           = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('reported_count', 'is_deleted', 'deleted_at')

    def create(self, validated_data):
        user, _ = User.objects.get_or_create(
            kakao_id=validated_data.get("kakao_id", None),
            defaults=validated_data)

        return user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['introduce',
                  'height',
                  'user',
                  'religion',
                  'drink_capacity',
                  'solo_reason',
                  'physical',
                  'job',
        ]

class PhoneUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["unique_id", "sendbird_id", "phone_number"]

    def create(self, validated_data):
        user, created = User.objects.get_or_create(
            phone_number=validated_data.get("phone_number"),
            defaults=validated_data)

        return user


class AuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthenticationNumber
        fields = '__all__'


class UserInterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInterest
        fields = "__all__"


class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = "__all__"

class UserImageSerializer(serializers.ListSerializer):
    class Meta:
        model = UserImage
        fields = "__all__"
