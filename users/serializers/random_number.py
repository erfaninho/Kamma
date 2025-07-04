from rest_framework import serializers

from utils.serializers import BaseSerializer
from utils.default_string import S

from ..models import UserRandomNumber


class UserCheckCodeRequestSerializer(BaseSerializer):
    """
        user login check code Request For Swagger
    """
    random_key = serializers.CharField(write_only=True, required=True)
    random_code = serializers.CharField(write_only=True, required=True)


class UserRandomNumberInfoSerializer(serializers.ModelSerializer):
    """
        Use this serializer for send code to parent for verify email or phone
    """

    class Meta:
        """
            Meta class
        """
        model = UserRandomNumber
        fields = (S.SEND_CODE_TYPE, S.TTL, S.KEY, S.RECEIVER, S.NUMBER)


class BaseUserResendCodeSerializer(BaseSerializer):
    """
        user forgot password send code
    """
    random_key = serializers.CharField(write_only=True, required=True)
    random_number = UserRandomNumberInfoSerializer(read_only=True)
    RANDOM_NUMBER_TITLE = None

    def create(self, validated_data: dict):
        """
            Resend verification code to user
        """
        self.random_number = UserRandomNumber.resend(title=self.RANDOM_NUMBER_TITLE,
                                                     key=validated_data.get(S.RANDOM_KEY))
        return self

