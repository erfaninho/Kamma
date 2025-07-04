from rest_framework import serializers

from users.models import User
from utils.default_string import S


class UserInfoSerializer(serializers.ModelSerializer):
    """
        info of user: id, avatar, avatar32, firstname, lastname
    """

    class Meta:
        """
            Meta class
        """
        model = User
        fields = ("__str__", S.ID, S.FIRST_NAME, S.LAST_NAME)


class UserRegisterInfoSerializer(serializers.ModelSerializer):
    """
        info of user: firstname, lastname, email, email_verified, phone_number, phon_verified
    """

    class Meta:
        """
            Meta class
        """
        model = User
        fields = (S.FIRST_NAME, S.LAST_NAME, S.EMAIL, S.VERIFIED_EMAIL, S.PHONE_NUMBER, S.VERIFIED_PHONE_NUMBER)