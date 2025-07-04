from django.core import validators
from django.db.models import Sum, Count
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_serializer_method
from phonenumber_field.serializerfields import PhoneNumberField

from rest_framework import serializers

from users.models import User, UserRandomNumber, UserToken
from orders.models import Order

from utils.default_string import S
from utils.serializers import BaseSerializer

from .base import UniquePhoneNumberField, UniqueEmailField
from .random_number import UserCheckCodeRequestSerializer, BaseUserResendCodeSerializer, UserRandomNumberInfoSerializer
from .user import UserRegisterInfoSerializer


class UserInfoSerializer(serializers.ModelSerializer):
    """
        Serializer for user indo edit
    """

    class Meta:
        model = User
        fields = [S.FIRST_NAME, S.LAST_NAME, S.BIRTH_DATE, S.PHONE_NUMBER, S.EMAIL]
        read_only_fields = [S.VERIFIED_EMAIL, S.VERIFIED_PHONE_NUMBER]


class UserProfileChangePasswordSerializer(BaseSerializer):
    """
        Serializer for user profile change password
    """
    password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs:dict):
        """
            Check user password
        """
        request = self.context[S.REQUEST]
        user:"User" = request.user
        if not user.check_password(attrs[S.PASSWORD]):
            raise validators.ValidationError({S.PASSWORD, _("Password is incorrect")})
        return attrs
    
    def create(self, validated_data):
        """
            Change User Password
        """
        request = self.context[S.REQUEST]
        user: "User" = request.user
        new_password = validated_data.get("new_password")
        user.validate_password(new_password, field_name="new_password")
        user.set_password(new_password)
        user.save(update_fields=(S.PASSWORD, S.UPDATE_DT))
        return user


class UserProfileLogoutSerializer(BaseSerializer):
    """
        Serializer to terminate user session token
    """
    def create(self, validated_data):
        """
            Delete token
        """
        request = self.context[S.REQUEST]
        user:"User" = request.user
        token:"UserToken" = request.auth
        if isinstance (token, UserToken):
            token.is_active = False
            token.save(update_fields=[S.IS_ACTIVE, S.UPDATE_DT])
        return user


class UserProfileChangeEmailRequestSerializer(BaseSerializer):
    email = serializers.EmailField()


class UserProfileChangePhoneNumberRequestSerializer(BaseSerializer):
    phone_number = PhoneNumberField()


class BaseUserProfileChangeDataSerializer(BaseSerializer):
    random_number = UserRandomNumberInfoSerializer(read_only=True)
    USE_USER = False
    FIELD_NAME = None
    VERIFIED_FIELD = None
    VERIFIED_ERROR_MESSAGE = None
    SEND_CODE_TYPE = None

    def create(self, validated_data: dict):
        request = self.context.get(S.REQUEST)
        user = request.user
        if self.USE_USER:
            receiver = getattr(user, self.FIELD_NAME)
            if self.VERIFIED_FIELD:
                if getattr(user, self.VERIFIED_FIELD):
                    message = self.VERIFIED_ERROR_MESSAGE or _("verified before")
                    raise validators.ValidationError(message, code="verified_before")
        else:
            receiver = validated_data.get(self.FIELD_NAME)
        self.random_number = UserRandomNumber.generate(user=user, title=UserRandomNumber.Title.CHANGE_DATA,
                                                       send_code_type=self.SEND_CODE_TYPE,
                                                       receiver=receiver)
        return self


class UserProfileChangeEmailSerializer(BaseUserProfileChangeDataSerializer):
    email = UniqueEmailField(write_only=True)
    FIELD_NAME = S.EMAIL
    SEND_CODE_TYPE = UserRandomNumber.AllTypes.EMAIL


class UserProfileChangePhoneNumberSerializer(BaseUserProfileChangeDataSerializer):
    phone_number = UniquePhoneNumberField(write_only=True)
    FIELD_NAME = S.PHONE_NUMBER
    SEND_CODE_TYPE = UserRandomNumber.AllTypes.SMS


class UserProfileCheckCodeSerializer(UserCheckCodeRequestSerializer):
    user_info = UserRegisterInfoSerializer(read_only=True)

    def create(self, validated_data: dict):
        request = self.context.get(S.REQUEST)
        user = request.user
        user_random_number = UserRandomNumber.check_number(title=UserRandomNumber.Title.CHANGE_DATA,
                                                           key=validated_data.get(S.RANDOM_KEY),
                                                           code=validated_data.get(S.RANDOM_CODE),
                                                           user=user)
        if user_random_number.send_code_type == UserRandomNumber.AllTypes.SMS:
            user.phone_number = user_random_number.receiver
            user.phone_verified = True
            user.save(update_fields=(S.PHONE_NUMBER, S.VERIFIED_PHONE_NUMBER, S.UPDATE_DT))
        if user_random_number.send_code_type == UserRandomNumber.AllTypes.EMAIL:
            user.email = user_random_number.receiver
            user.email_verified = True
            user.save(update_fields=(S.EMAIL, S.VERIFIED_EMAIL, S.UPDATE_DT))
        self.user_info = user
        return self


class ProfileDashboardSerializer(BaseSerializer):

    user = serializers.SerializerMethodField()

    @swagger_serializer_method(serializer_or_field=serializers.CharField)
    def get_user(self, obj: "User"):
        return obj.get_full_name()