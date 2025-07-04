from rest_framework import serializers

from users.models import Address

from utils.default_string import S


class AddressSerializer(serializers.ModelSerializer):
    """
        Address serializer to assign addresses to users
    """

    class Meta:
        model = Address
        fields = [S.ID, S.TITLE, S.POST_CODE, S.STATE, S.CITY, S.POSTAL_ADDRESS, S.LATITUDE, S.LONGITUDE,
                  S.USER, S.PHONE_NUMBER,]


class AddressCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [S.TITLE, S.POST_CODE, S.STATE, S.CITY, S.POSTAL_ADDRESS, S.LATITUDE, S.LONGITUDE,
                  S.PHONE_NUMBER]

    def create(self, validated_data):
        validated_data['user'] = self.context[S.REQUEST].user
        return super().create(validated_data)


class OrderAddressSerializer(serializers.ModelSerializer):
    """
        Address serializer to assign addresses to users
    """

    class Meta:
        model = Address
        fields = [S.ID, S.TITLE, S.POST_CODE, S.STATE, S.CITY, S.POSTAL_ADDRESS, S.LATITUDE, S.LONGITUDE]
