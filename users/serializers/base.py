from django.utils.translation import gettext_lazy as _
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from users.models import User, UserRandomNumber

from utils.serializers import BaseSerializer
from utils.default_string import S


class UniquePhoneNumberField(PhoneNumberField):

    def __init__(self, *args, region=None, **kwargs):
        super().__init__(*args, region=region, **kwargs)
        self.validators.append(UniqueValidator(queryset=User.objects.filter(is_active=True),
                                               message=_("duplicate phone number")))
        self.required = True


class UniqueEmailField(serializers.EmailField):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.validators.append(UniqueValidator(queryset=User.objects.filter(is_active=True),
                                               message=_("duplicate email")))