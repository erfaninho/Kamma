from django.db import models
from django_autoutils.model_utils import AbstractModel
from django.utils.translation import gettext_lazy as _

from utils.default_string import S, D

from products.models import ProductInstance
from users.models import User, Address


class Order (AbstractModel):
    """
        Order Model for users
    """
    class OrderStatus(models.IntegerChoices):
        PENDING = 1, "Pending"
        PAID = 2, "Paid"
        SHIPPED = 3, "Shipped"
        COMPLETED = 4, "Completed"
        CANCELLED = 5, "Cancelled"

    user = models.ForeignKey(User, verbose_name=_("user"), on_delete=models.NOT_PROVIDED, related_name="orders")
    order_status = models.IntegerChoices(choices=OrderStatus.choices, default=OrderStatus.PENDING)
    number = models.PositiveIntegerField(_("number"))
    total_amount = models.PositiveIntegerField(_("total_amount"))
    shipping_address = models.ForeignKey(Address, verbose_name=_("shipping_address"), on_delete=models.CASCADE)

    def __str__(self):
        return f"Order {self.number}: {self.user}"
    
    def total_amount_calculate(self, *args, **kwargs):
        for item in self.items.all():
            self.total_amount += item.total_amount
        self.save(*args, **kwargs, update_fields=[S.TOTAL_AMOUNT])

    class Meta:
        db_name = D.ORDER
        verbose_name = _("order")
        verbose_name_plural = _("orders")


class OrderItem(AbstractModel):
    """
        Order Item model for orders
    """
    order = models.ForeignKey(Order, verbose_name=_("order"), on_delete=models.PROTECT, related_name="items")
    product = models.ForeignKey(ProductInstance, verbose_name=_("product"), on_delete=models.PROTECT, related_name="orders")
    count = models.PositiveSmallIntegerField(_("count"))
    total_amount = models.PositiveIntegerField(_("total_amount"))

    def save(self, *args, **kwargs):
        self.total_amount = self.product.product.price * self.count
        super().save(*args, **kwargs, update_fields=[S.TOTAL_AMOUNT])

    class Meta:
        db_name = D.ORDER_ITEM
        verbose_name = _("order_item")
        verbose_name_plural = _("order_items")
