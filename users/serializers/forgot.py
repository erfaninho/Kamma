from rest_framework import serializers, exceptions

from utils.serializers import BaseSerializer
from utils.default_string import S

from .random_number import BaseUserResendCodeSerializer
from .login import UserRandomNumberInfoSerializer

from ..models import User, UserRandomNumber

from django.utils.translation import gettext_lazy as _


class UserForgotStartRequestSerializer(BaseSerializer):
    """
        user forgot password start process Request For Swagger
    """
    username = serializers.CharField(write_only=True, required=True)


class UserForgotStartSerializer(BaseSerializer):
    """
        user forgot password start process
    """
    username = serializers.CharField(write_only=True, required=True)

    random_number = UserRandomNumberInfoSerializer(read_only=True)

    def create(self, validated_data: dict):
        """
            User forgot password start process
        """
        username = validated_data.get(S.USERNAME).lower()
        send_code_type = None
        user: "User" = User.objects.filter(phone_number=username, is_active=True, phone_verified=True).first()
        if user:
            send_code_type = UserRandomNumber.AllTypes.SMS
        else:
            user: "User" = User.objects.filter(email=username, is_active=True, email_verified=True).first()
            if user:
                send_code_type = UserRandomNumber.AllTypes.EMAIL
        if send_code_type is None:
            raise exceptions.ValidationError(_("invalid input data"))
        self.random_number = UserRandomNumber.generate(user=user, title=UserRandomNumber.Title.USER_FORGOT,
                                                       send_code_type=send_code_type)
        return self


class UserResendCodeRequestSerializer(BaseSerializer):
    random_key = serializers.CharField(write_only=True, required=True)


class UserForgotResendCodeSerializer(BaseUserResendCodeSerializer):
    """
        user forgot password send code
    """
    RANDOM_NUMBER_TITLE = UserRandomNumber.Title.USER_FORGOT


class UserForgotChangePasswordSerializer(BaseSerializer):
    """
        user forgot check code
    """
    random_key = serializers.CharField(write_only=True, required=True)
    random_code = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True)

    def create(self, validated_data: dict):
        """
            Check verification code and login user
        """
        user_random_number = UserRandomNumber.check_number(title=UserRandomNumber.Title.USER_FORGOT,
                                                           key=validated_data.get(S.RANDOM_KEY),
                                                           code=validated_data.get(S.RANDOM_NUMBER),
                                                           disable=False)
        password = validated_data.get(S.PASSWORD)
        user = user_random_number.user
        user.validate_password(password)
        user.set_password(password)
        user.save(update_fields=(S.PASSWORD, S.UPDATE_DT))

        user_random_number.is_valid = False
        user_random_number.save()

        user.clear_tokens()
        return user