from django.contrib import admin

from .models import Order, OrderItem

from utils.default_string import S


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
        Order Model Admin Panel
    """

    list_display = [S.NUMBER, S.USER, S.ORDER_STATUS, S.TOTAL_AMOUNT]
    list_filter = [S.USER, S.ORDER_STATUS]
    search_fields = [S.USER, S.NUMBER]

    fieldsets = (
        (None, {
            "fields": (
                S.NUMBER, S.USER, S.ORDER_STATUS, S.TOTAL_AMOUNT, S.SHIPPING_ADDRESS
            ),
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin (admin.ModelAdmin):
    """
        Order Item Admin Model
    """

    list_display = [S.ORDER, S.PRODUCT, S.COUNT]
    list_filter = [S.ORDER, S.PRODUCT]
    search_fields = [S.ORDER, S.PRODUCT]

    fieldsets = (
        (None, {
            "fields": (
                S.ORDER, S.PRODUCT, S.COUNT, S.TOTAL_AMOUNT
            ),
        }),
    )
    