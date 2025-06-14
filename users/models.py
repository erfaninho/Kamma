from django.db import models
from django_autoutils.model_utils import AbstractModel
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from utils.default_string import S, D
from products.models import ProductInstance

import random


class User(AbstractUser):
    """
        Model for users
    """
    REQUIRED_FIELDS = ['username', 'email', 'phone_number', 'first_name', 'last_name']
    first_name = models.CharField(_("first_name"), max_length=50)
    last_name = models.CharField(_("last_name"), max_length=50)
    username = models.CharField(_("username"), max_length=50, unique=True)

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
    
    def __str__(self):
        return self.get_full_name()
    
    class Meta:
        db_table = D.USER
        verbose_name = _('user')
        verbose_name_plural = _('userS')
        constraints = [
            models.UniqueConstraint(fields=[S.EMAIL], violation_error_message=_("User with this email already exists")),
            models.UniqueConstraint(fields=[S.PHONE_NUMBER], violation_error_message=_("User with this phone number already exists"))
        ]


class Address(AbstractModel):
    """
        Address Model for user addresses
    """
    user = models.ForeignKey(User, verbose_name=_("user"), on_delete=models.CASCADE, related_name="adresses")
    title = models.CharField(_("title"), max_length=255)
    post_code = models.CharField(_("post_code"), max_length=10)
    state = models.CharField(_("state"), max_length=50)
    city = models.CharField(_("city"), max_length=50)
    latitude = models.DecimalField(_('latitude'), max_digits=10, decimal_places=6)
    longitude = models.DecimalField(_('longitude'), max_digits=10, decimal_places=6)
    postal_address = models.TextField(_("postal_address"))
    is_default = models.BooleanField(_("is_default"), default=True)

    class Meta:
        db_name = D.ADDRESS
        verbose_name = _("address")
        verbose_name_plural = _("addresses")
    
    def __str__(self):
        return f'{self.user}:{self.title}'
    
    def save(self, *args, **kwargs):
        if self.pk is None:
            old_address = self.user.get_default_address().last()
            if old_address:
                old_address.is_default = False
                old_address.save(updated_fields=[S.IS_DEFAULT])
        
        super().save(*args, **kwargs, update_fields=[S.IS_DEFAULT])
    

class UserRandomNumber(AbstractModel):
    """
        Generate random number for user verification
    """

    user = models.ForeignKey(User, verbose_name=_("user"), on_delete=models.CASCADE, related_name="user_random_numbers")
    is_active = models.BooleanField(_("is_active"), default=True)
    number = models.CharField(_("number"), max_length=6)

    def save(self, *args, **kwargs):
        number = ""
        for i in range(6):
            number = number+str(random.randint(0,9))
        self.number = number
        return super().save(*args, **kwargs, update_fields=[S.NUMBER])
    
    def __str__(self):
        return f'{self.user}:{self.number}'
    
    class Meta:
        db_name = D.USER_RANDOM_NUMBER
        verbose_name = _("user_random_number")
        verbose_name_plural = _("user_random_numbers")


class Cart(AbstractModel):
    """
        Cart Model for user
    """

    user = models.ForeignKey(User, verbose_name=_("cart"), on_delete=models.CASCADE, related_name="cart")
    total_amount = models.PositiveBigIntegerField(verbose_name=_("total_amount"))

    def __str__(self):
        return self.user
    
    def calculate_total_amount(self, *args, **kwargs):
        for item in self.items.all():
            self.total_amount += item.total_price
        
        self.save(*args, **kwargs,update_fields=[S.TOTAL_AMOUNT])
    
    class Meta:
        db_name = D.CART
        verbose_name = _("cart")
        verbose_name_plural = _("carts")
    

class CartItem(AbstractModel):
    """
        Cart Item for user
    """

    cart = models.ForeignKey(Cart, verbose_name=_("cart"), on_delete=models.CASCADE, related_name="items")
    product_instance = models.ForeignKey(ProductInstance, verbose_name=_("product_instance"), on_delete=models.CASCADE, related_name="cart_item")
    count = models.PositiveSmallIntegerField(_("count"))
    total_amount = models.PositiveIntegerField(_("total_amount"))

    def __str__(self):
        return f'{self.cart.user}:{self.product_instance.product}'
    
    def calculate_total_amount(self, *args, **kwargs):
        self.total_amount = self.product_instance.product.price * self.count

        super().save(*args, **kwargs, update_fields=[S.TOTAL_AMOUNT])

    class Meta:
        db_name = D.CART_ITEM
        verbose_name = _("cart_item")
        verbose_name_plural = _("cart_items")