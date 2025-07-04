from django.contrib import auth
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, exceptions

from django.utils import timezone

from users.models import User, UserToken, UserRandomNumber
from utils.serializers import BaseSerializer
from utils.default_string import S
from .random_number import UserRandomNumberInfoSerializer, UserCheckCodeRequestSerializer


class UserTokenInfoSerializer(serializers.ModelSerializer):
    """
        info of user token
    """

    class Meta:
        """
            Meta class
        """
        model = UserToken
        fields = (S.TOKEN,)


class UserLoginStartSerializer(BaseSerializer):
    """
        user login check password
    """
    username = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)

    token_info = UserTokenInfoSerializer(read_only=True)
    random_number = serializers.CharField(read_only=True)
    random_key = serializers.CharField(read_only=True)
    receiver = serializers.CharField(read_only=True)


    User = auth.get_user_model()

    def validate(self, attrs):
        username = attrs["username"]
        password = attrs["password"]
        request = self.context.get("request")

        user = None

        try:
            if "@" in username:
                user = self.User.objects.filter(email=username).first()
                send_method = UserRandomNumber.AllTypes.EMAIL
                receiver = user.email
            else:
                user = self.User.objects.filter(phone_number=username).first()
                send_method = UserRandomNumber.AllTypes.SMS
                receiver = user.phone_number
        except User.DoesNotExist:
            raise serializers.ValidationError("User Does Not Exist")
        
        if not user.check_password(password):
            raise serializers.ValidationError("Incorrect Login Details")
        
        self.user = user
        self.send_method = send_method
        self.receiver = receiver
        return attrs
    
    def create(self, validated_data):
        user = self.user
        send_method = self.send_method
        receiver = self.receiver

        random_number = UserRandomNumber.objects.create(
            user = user,
            title = UserRandomNumber.Title.USER_LOGIN,
            send_code_type = send_method,   
            receiver = receiver,
        )
        temp_token = UserToken.create_temporary_token(user=user)

        return {
            "random_number": random_number.number,
            "random_key": random_number.key,
            "receiver": random_number.receiver,
            "token_info": temp_token
        }


class UserLoginStepTwoSerializer(BaseSerializer):
    """
        Serializer to approve to step login
    """
    random_key = serializers.CharField()
    random_number = serializers.CharField()
    temp_token = serializers.CharField()

    token = UserTokenInfoSerializer(read_only=True)

    def validate(self, attrs):
        key = attrs["random_key"]
        number = attrs["random_number"]
        temp_token = attrs["temp_token"]

        user_token = UserToken.objects.get(token=temp_token)
        if not user_token or user_token.expire_dt<timezone.now():
            raise serializers.ValidationError("temporary token invalid or expired")
        
        user = temp_token.user

        try:
            random_number = UserRandomNumber.check_number(title=UserRandomNumber.Title.USER_LOGIN, key=key, number=number, user=user)
        except Exception:
            raise ("Wrong or Invalid Code")
        
        self.user = user
        return attrs
    
    def create(self, validated_data):
        token = UserToken.create_token(user=self.user)
        return {"token":token}
    
