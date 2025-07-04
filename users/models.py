import logging
import datetime

from django.db import models
from django_autoutils.model_utils import AbstractModel
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils.functional import cached_property
from django.core.mail import send_mail
from django.core import validators
from django_autoutils.utils import handle_validation_error

from constance import config

from phonenumber_field.modelfields import PhoneNumberField

from rest_framework import exceptions

from utils.default_string import S, D
from utils.server_utils import temp_token_expire_dt_generator, token_expire_dt_generator, number_generator, \
    token_generator
from products.models import ProductInstance


class User(AbstractUser):
    """
        Model for users
    """
    class UserType(models.IntegerChoices):
        DEVELOPER = 1, _("Developer")
        ADMIN = 2, _("Admin")
        CUSTOMER = 3, _("Customer")

    REQUIRED_FIELDS = [S.EMAIL, S.PHONE_NUMBER, S.FIRST_NAME, S.LAST_NAME, S.USER_TYPE]
    first_name = models.CharField(_("first_name"), max_length=50)
    last_name = models.CharField(_("last_name"), max_length=50)
    user_type = models.IntegerField(_("user_type"), choices=UserType.choices, default=UserType.CUSTOMER)

    email = models.EmailField(_("email"), max_length=254, unique=True)
    verified_email = models.BooleanField(_("verified_email"), default=False)

    phone_number = PhoneNumberField(_("phone_number"))
    verified_phone_number = models.BooleanField(_("verified_phone_number"), default=False)

    birth_date = models.DateField(_("birth_date"), auto_now=False, auto_now_add=False, null=True, blank=True)

    def get_full_name (self):
        full_name = f'{self.first_name} {self.last_name}'
        return full_name.strip()
    
    def get_default_address(self):
        return self.addresses.filter(is_default=True)
    
    def validate_password(self, password: str, field_name: str = S.PASSWORD):
        try:
            validate_password(password, self)
        except validators.ValidationError as e:
            handle_validation_error(e, field_name)

    def login(self) -> "UserToken":
        self.last_login = timezone.now()
        self.save(update_fields=(S.UPDATE_DT))
        return UserToken.create_token(user=self)
        
    def __str__(self):
        return self.get_full_name()
    
    class Meta:
        db_table = D.USER
        verbose_name = _('user')
        verbose_name_plural = _('userS')
        constraints = [
            models.UniqueConstraint(name=f'{S.EMAIL}_Unique', fields=[S.EMAIL], violation_error_message=_("User with this email already exists")),
            models.UniqueConstraint(name=f"{S.PHONE_NUMBER}_Unique", fields=[S.PHONE_NUMBER], violation_error_message=_("User with this phone number already exists"))
        ]


class Address(AbstractModel):
    """
        Address Model for user addresses
    """
    user = models.ForeignKey(User, verbose_name=_("user"), on_delete=models.CASCADE, related_name="addresses")
    title = models.CharField(_("title"), max_length=255)
    post_code = models.CharField(_("post_code"), max_length=10)
    state = models.CharField(_("state"), max_length=50)
    city = models.CharField(_("city"), max_length=50)
    latitude = models.DecimalField(_('latitude'), max_digits=10, decimal_places=6)
    longitude = models.DecimalField(_('longitude'), max_digits=10, decimal_places=6)
    postal_address = models.TextField(_("postal_address"))
    is_default = models.BooleanField(_("is_default"), default=True)

    class Meta:
        db_table = D.ADDRESS
        verbose_name = _("address")
        verbose_name_plural = _("addresses")
    
    def __str__(self):
        return f'{self.user}:{self.title}'
    
    def save(self, *args, **kwargs):
        if self.pk is not None:
            old_address = self.user.get_default_address().last()
            if old_address:
                old_address.is_default = False
                old_address.save(updated_fields=[S.IS_DEFAULT])
        
        super().save(*args, **kwargs)
    

class UserRandomNumber(AbstractModel):
    """
        Generate random number for user verification
    """
    class AllTypes(models.TextChoices):
        SMS = "SMS", _("SMS")
        EMAIL = "EMAIL", _("EMAIL")

    user = models.ForeignKey(User, verbose_name=_("user"), on_delete=models.CASCADE, related_name="user_random_numbers")
    is_active = models.BooleanField(_("is active"), default=True)
    number = models.CharField(_("number"), default=number_generator, null=True, blank=True)
    title = models.CharField(_("title"), max_length=50)
    ttl = models.PositiveSmallIntegerField(_("ttl"), default=180)
    wrong_attempts = models.PositiveSmallIntegerField(_("wrong attempts"), default=0,)
    key = models.CharField(_("key"), default=token_generator, max_length=100, unique=100)
    receiver = models.CharField(_("receiver"), max_length=100)
    send_code_type = models.CharField(_("send code type"), max_length=50, choices=AllTypes.choices, default=AllTypes.EMAIL)

    def __str__(self):
        return f'{self.user}:{self.number}'
    
    class Meta:
        db_table = D.USER_RANDOM_NUMBER
        verbose_name = _("user_random_number")
        verbose_name_plural = _("user_random_numbers")

    class Title:
        """
            All titles
        """
        USER_LOGIN = "user_login"
        USER_FORGOT = "user_forgot"
        REGISTER_PARENT = "register_customer"
        CHANGE_DATA = "change_data"

    @cached_property
    def expire_time (self):
        """
            Expire time for the number
        """
        if self.insert_dt is None:
            return None
        return self.insert_dt + timezone.timedelta(seconds=self.ttl)

    def is_expired (self):
        return timezone.now() > self.insert_dt + datetime.timedelta(seconds=self.ttl)
    
    def deactivate (self):
        if self.is_active and self.is_expired():
            self.is_active = False
            self.save(updated_fields = [S.IS_ACTIVE])
    
    @classmethod
    def get(cls, title:str, key:str, user:"User", ) -> "UserRandomNumber":
        """
            Get User Random Number
        """
        random_number: "UserRandomNumber" = cls.objects.filter(title=title, is_active=True, key=key).first()
        if random_number is None or (user and random_number.user != user):
            raise exceptions.ValidationError(_("not_found"), code="not_found")
        return random_number
    
    @classmethod
    def resend(cls, title: str, key: str, send_code_type: str = None) -> "UserRandomNumber":
        """
            Resend random number
        """
        random_number = cls.get(title=title, key=key)
        return random_number.resend_number(send_code_type=send_code_type)

    def resend_number(self, send_code_type: str = None) -> "UserRandomNumber":
        """
            Resend a random number
        """
        if self.insert_dt + timezone.timedelta(minutes=1) > timezone.now():
            raise exceptions.ValidationError(_("too fast request, try again one minute later"), code="too_fast_request")
        if send_code_type is None:
            send_code_type = self.send_code_type
        else:
            self.receiver = None
        return self.generate(user=self.user, receiver=self.receiver, title=self.title,
                             ttl=self.ttl, send_code_type=send_code_type)
    
    @classmethod
    def generate(cls, user:"User", title:str, ttl:int, receiver:str=None, send_code_type:str = AllTypes.EMAIL):
        ttl=180
        if send_code_type == cls.AllTypes.EMAIL:
            receiver = user.email
        elif send_code_type == cls.AllTypes.SMS:
            receiver = user.phone_number
        cls.objects.filter(user=user, title=title).update(is_active=False)
        user_random_number : "UserRandomNumber" = cls.objects.create(
            user=user, title=title, ttl=ttl, receiver=receiver, send_code_type=send_code_type
        )
        user_random_number.send_number()
        return user_random_number

    @classmethod
    def check_number(cls, title:str, key:str, number:str, disable=True, user: "User" = None) -> "UserRandomNumber":
        """
            Check input Number
        """
        user_random_number = cls.get(title=title, key=key, user=user)
        if user_random_number.expire_time < timezone.now():
            raise exceptions.ValidationError(_("verification Code is Expired"), code="expire_code")
        if user_random_number.wrong_attempts> config.USER_WRONG_ATTEMPTS_MAX:
            raise exceptions.ValidationError(_("You reached Maximum Number of Wrong Attempts"), code="max_wrong_attempts")
        
        if user_random_number.number != number:
            user_random_number.wrong_attempts += 1
            user_random_number.save(update_fields=[S.WRONG_ATTEMPTS])
            raise exceptions.ValidationError(_("Wrong Input, Try Again"), code="wrong_input")

        if disable:
            user_random_number.is_active = False
            user_random_number.save(update_fields=[S.IS_ACTIVE])
        return user_random_number
    
    @property
    def message(self):
        """
            Message to be sent
        """
        return f'Your verification code is {self.number}'
    
    def send_number(self):
        self.log(logging.INFO, f'starting send code to {self.receiver}')
        if self.send_code_type == self.AllTypes.EMAIL:
            self.send_number_email()
        elif self.send_code_type == self.AllTypes.SMS:
            self.send_number_sms()
        self.log(logging.INFO, f'sent code to {self.receiver}')
    
    def send_number_email(self):
        """
            Send Number With Email
        """
        try:
            subject = "Verification Code Kamma"
            send_mail(subject=subject, message=self.message, from_email=None, recipient_list=[self.receiver])
        except Exception as e:
            self.log(logging.ERROR, f"can not send email. error: {e}")
            raise exceptions.ValidationError(_("can not send email. call support"), code="send_email_error")
    
    def send_number_sms(self):
        """
            Send Number with SMS
        """
        pass


class UserToken (AbstractModel):
    """
        User Token Model to store authentication tokens
    """

    user = models.ForeignKey(User, verbose_name=_("user"), on_delete=models.CASCADE, related_name="tokens")
    token = models.CharField(_("token"), max_length=100, unique=True, db_index=True, default=token_generator)
    is_temp = models.BooleanField(_("is_temp"), default=False)
    expire_dt = models.DateTimeField(_("expire_time"), auto_now=False, auto_now_add=False)

    class Meta:
        db_table = D.USER_TOKEN
        verbose_name = "user_token"
        verbose_name_plural = "user_tokens"

    def __str__(self):
        return f'token {self.id} ({self.user})'
    
    @classmethod
    def create_token(cls, user: User) -> "UserToken":
        cls.objects.filter(user=user, is_temp=True).update(is_active=False)
        return cls.objects.create(
            user=user,
            is_temp=False,
            expire_dt=token_expire_dt_generator()
        )
    
    @classmethod
    def create_temporary_token(cls, user:User) -> "UserToken":
        return cls.objects.create(
            user=user,
            is_temp=True,
            expire_dt=temp_token_expire_dt_generator()
            )


class Cart(AbstractModel):
    """
        Cart Model for user
    """

    user = models.ForeignKey(User, verbose_name=_("cart"), on_delete=models.CASCADE, related_name="cart")
    total_amount = models.PositiveBigIntegerField(verbose_name=_("total_amount"), null=True, blank=True)

    def __str__(self):
        return f'{self.user}'
    
    def calculate_total_amount(self, *args, **kwargs):
        for item in self.items.all():
            self.total_amount += item.total_amount
        
        self.save(*args, **kwargs,update_fields=[S.TOTAL_AMOUNT])
    
    class Meta:
        db_table = D.CART
        verbose_name = _("cart")
        verbose_name_plural = _("carts")
    

class CartItem(AbstractModel):
    """
        Cart Item for user
    """

    cart = models.ForeignKey(Cart, verbose_name=_("cart"), on_delete=models.CASCADE, related_name="items")
    product_instance = models.ForeignKey(ProductInstance, verbose_name=_("product_instance"), on_delete=models.CASCADE, related_name="cart_item")
    count = models.PositiveSmallIntegerField(_("count"))
    total_amount = models.PositiveIntegerField(_("total_amount"), null=True, blank=True)

    def __str__(self):
        return f'{self.cart.user}:{self.product_instance.product}'
    
    def calculate_total_amount(self, *args, **kwargs):
        self.total_amount = self.product_instance.product.price * self.count

        super().save(*args, **kwargs, update_fields=[S.TOTAL_AMOUNT])

    class Meta:
        db_table = D.CART_ITEM
        verbose_name = _("cart_item")
        verbose_name_plural = _("cart_items")


class SessionCart(AbstractModel):
    """
        Session Cart for handling not logged in users carts
    """

    session = models.CharField(_("session"), max_length=255)
    total_amount = models.PositiveIntegerField(_("total amount"), default=0)

    def __str__(self):
        return f'{self.session}'
    
    def calculate_total_amount(self, *args, **kwargs):
        for item in self.items.all():
            self.total_amount += item.total_amount
        
        self.save(*args, **kwargs,update_fields=[S.TOTAL_AMOUNT])
    
    class Meta:
        db_table = D.SESSION_CART
        verbose_name = _("session_cart")
        verbose_name_plural = _("session_carts")


class SessionCartItem(AbstractModel):
    """
        Cart Item for not logged in user
    """

    session_cart = models.ForeignKey(SessionCart, verbose_name=_("session cart"), on_delete=models.CASCADE, related_name="items")
    product_instance = models.ForeignKey(ProductInstance, verbose_name=_("product instance"), on_delete=models.CASCADE, related_name="session_cart_item")
    count = models.PositiveSmallIntegerField(_("count"))
    total_amount = models.PositiveIntegerField(_("total_amount"), null=True, blank=True)

    def __str__(self):
        return f'{self.session_cart}:{self.product_instance.product}'
    
    def calculate_total_amount(self, *args, **kwargs):
        self.total_amount = self.product_instance.product.price * self.count

        super().save(*args, **kwargs, update_fields=[S.TOTAL_AMOUNT])

    class Meta:
        db_table = D.SESSION_CART_ITEM
        verbose_name = _("session_cart_item")
        verbose_name_plural = _("session_cart_items")