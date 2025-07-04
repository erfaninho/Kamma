from django.utils import timezone
from constance import config
from autoutils.script import id_generator
import string


def token_expire_dt_generator():
    """
        Generate expire date time field for user token
    """
    return timezone.now()+timezone.timedelta(days=config.USER_TOKEN_EXPIRE_DAY)


def temp_token_expire_dt_generator():
    """
        Generate expire date time field for user temp token
    """
    return timezone.now()+timezone.timedelta(minutes=config.USER_TEMP_TOKEN_EXPIRE_MINUTE)


def number_generator(chars=string.digits):
    """
        Generate Random numbers for user Authentication
    """
    return id_generator(size=config.USER_RANDOM_NUMBER_LENGTH, chars=chars)


def token_generator():
    """
        Generate a token for user authorization by configurable size
    """
    return id_generator(size=config.USER_TOKEN_LENGTH)
