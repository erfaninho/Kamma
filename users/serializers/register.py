from rest_framework import serializers

from django_autoutils.serializer_utils import get_current_user_default
from django_autoutils.utils import handle_validation_error

from django.core import validators

from ..models import User, UserToken, UserRandomNumber

from .login import UserTokenInfoSerializer
from .random_number import UserRandomNumberInfoSerializer
from .user import UserRegisterInfoSerializer
from .base import *

from utils.serializers import BaseSerializer
from utils.default_string import S


class RegisterSerializer (serializers.ModelSerializer):
    """
        Serializer for user registration process
    """
    token_info = UserTokenInfoSerializer(read_only=True)

    def create(self, validated_data: dict):
        """
            Register User
        """
        user = User(**validated_data, is_active=False)
        try:
            user.full_clean()
        except validators.ValidationError as e:
            handle_validation_error(e)
        user_token = UserToken.create_temporary_token(user=user)
        user.token_info = user_token
        return user


class UserRandomNumberInfoSerializer (serializers.ModelSerializer):
    """
        Serializer to parse user random Number Info
    """

    class Meta:
        model = UserRandomNumber
        fields = [S.USER, S.TTL, S.KEY, S.NUMBER]


class UserCheckCodeRequestSerializer(BaseSerializer):
    """
        user login check code Request For Swagger
    """
    random_key = serializers.CharField(write_only=True, required=True)
    random_code = serializers.CharField(write_only=True, required=True)


class RegisterUserSendCodeRequestSerializer(BaseSerializer):
    """
        Use this serializer for send code to user for verify email or phone request body (For swagger)
    """
    user = get_current_user_default()


class RegisterUserSendCodeSerializer(BaseSerializer):
    """
        Use this serializer for send code to user for verify email or phone
    """
    user = get_current_user_default()
    random_number = UserRandomNumberInfoSerializer(read_only=True)

    def create(self, validated_data: dict):
        """
            Register a user and send email verification
        """
        self.random_number = UserRandomNumber.generate(user=validated_data.get(S.USER),
                                                       title=UserRandomNumber.Title.REGISTER_PARENT,
                                                       send_code_type=validated_data.get(S.SEND_CODE_TYPE))
        return self


class RegisterUserCheckCodeRequestSerializer(BaseSerializer):
    """
        Use this serializer for check code for verify email or phone Request body for swagger
    """
    random_key = serializers.CharField(write_only=True, required=True)
    random_code = serializers.CharField(write_only=True, required=True)


class RegisterUserCheckCodeSerializer(BaseSerializer):
    """
        Use this serializer for check code for verify email or phone
    """
    user_info = UserRegisterInfoSerializer(read_only=True)
    random_key = serializers.CharField(write_only=True, required=True)
    random_code = serializers.CharField(write_only=True, required=True)

    def create(self, validated_data: dict):
        """
            Register a user and send email verification
        """
        user_random_number = UserRandomNumber.check_number(title=UserRandomNumber.Title.REGISTER_PARENT,
                                                           key=validated_data.get(S.RANDOM_KEY),
                                                           code=validated_data.get(S.RANDOM_NUMBER))
        user = user_random_number.user
        send_code_type = user_random_number.send_code_type
        if send_code_type in {UserRandomNumber.AllTypes.SMS}:
            user.verfied_phone_number = True
            user.save(update_fields=(S.VERIFIED_PHONE_NUMBER, S.UPDATE_DT))
        elif send_code_type in {UserRandomNumber.AllTypes.EMAIL}:
            user.verified_email = True
            user.save(update_fields=(S.VERIFIED_EMAIL, S.UPDATE_DT))
        self.user_info = user_random_number.user
        return self
    

class RegisterUserSetPasswordRequestSerializer(BaseSerializer):
    """
        Use this serializer for set user password after verify phone or email Request body for Swagger
    """
    password = serializers.CharField(write_only=True)


class RegisterUserSetPasswordSerializer(RegisterUserSetPasswordRequestSerializer):
    """
        Use this serializer for set user password after verify phone or email
    """
    user_info = UserRegisterInfoSerializer(read_only=True)
    token_info = UserTokenInfoSerializer(read_only=True)

    def create(self, validated_data: dict):
        """
            Register a user and send email verification
        """
        request = self.context.get(S.REQUEST)
        user: "User" = request.user
        password = validated_data.get(S.PASSWORD)
        user.password = password
        user.is_active = True
        user.save(update_fields=(S.PASSWORD, S.IS_ACTIVE, S.UPDATE_DT))
        self.user_info = user
        user_token = UserToken.create_token(user=user)
        self.token_info = user_token
        return self
