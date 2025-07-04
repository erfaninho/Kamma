from django.db import models
from django.utils import timezone
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
        PENDING = 1, _("Pending")
        PAID = 2, _("Paid")
        SHIPPED = 3, _("Shipped")
        COMPLETED = 4, _("Completed")
        CANCELLED = 5, _("Cancelled")
        FAILED = 6, _("Failed")

    user = models.ForeignKey(User, verbose_name=_("user"), on_delete=models.SET_NULL, related_name="orders", null=True)
    order_status = models.IntegerField(choices=OrderStatus.choices, default=OrderStatus.PENDING)
    number = models.CharField(_("number"), null=True, blank=True, max_length=50)
    total_amount = models.PositiveIntegerField(_("total_amount"), null=True, blank=True)
    shipping_address = models.ForeignKey(Address, verbose_name=_("shipping_address"), on_delete=models.CASCADE)

    def __str__(self):
        return f"Order {self.number}: {self.user}"
    
    def total_amount_calculate(self, *args, **kwargs):
        total = sum(item.total_amount for item in self.items.all())
        self.total_amount = total
        self.save(update_fields=["total_amount"])

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.number = f"ORD-{timezone.now().strftime("%Y%m%d")}-{len(Order.objects.all())+1:08d}"
            super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

    class Meta:
        db_table = D.ORDER
        verbose_name = _("order")
        verbose_name_plural = _("orders")


class OrderItem(AbstractModel):
    """
        Order Item model for orders
    """
    order = models.ForeignKey(Order, verbose_name=_("order"), on_delete=models.PROTECT, related_name="items")
    product = models.ForeignKey(ProductInstance, verbose_name=_("product"), on_delete=models.PROTECT, related_name="orders")
    count = models.PositiveSmallIntegerField(_("count"))
    total_amount = models.PositiveIntegerField(_("total_amount"), null=True, blank=True)

    def save(self, *args, **kwargs):
        self.total_amount = self.product.product.price * self.count
        super().save(*args, **kwargs)
        self.order.total_amount_calculate()

    class Meta:
        db_table = D.ORDER_ITEM
        verbose_name = _("order_item")
        verbose_name_plural = _("order_items")


class Payment(AbstractModel):
    """
        Payment Model to Store User Payments
    """
    class PaymentStatus(models.IntegerChoices):
        NEW = 1, _("New")
        FAILED = 2, _("Failed")
        SUCCESSFUL = 3, _("Successful")

    user = models.ForeignKey(User, verbose_name=_("user"), null=True, on_delete=models.SET_NULL, related_name='payments') 
    order = models.OneToOneField(Order, verbose_name=_("order"), on_delete=models.PROTECT, related_name='payment')
    payment_status = models.IntegerField(choices=PaymentStatus.choices, default=PaymentStatus.NEW)

    def __str__(self):
        return f'{self.user}:{self.order}'

