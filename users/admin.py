from django.contrib import admin
from .models import *

from utils.default_string import S


@admin.register(User)
class UserAdmin (admin.ModelAdmin):
    list_display = [S.PHONE_NUMBER, S.EMAIL, S.USERNAME]
    search_fields = [S.PHONE_NUMBER, S.LAST_NAME, S.USERNAME, S.EMAIL]

    fieldsets = (
        (None, {
            'fields' : (S.FIRST_NAME, S.LAST_NAME, S.USERNAME, S.EMAIL, S.VERIFIED_EMAIL, S.PHONE_NUMBER, S.VERIFIED_PHONE_NUMBER, S.BIRTH_DATE )
        }),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = [S.USER, S.TITLE, S.POST_CODE, S.IS_DEFAULT]
    search_fields = [S.USER, S.TITLE, S.POST_CODE, S.POSTAL_ADDRESS]
    list_filter = [S.USER, S.IS_DEFAULT]

    fieldsets = (
        (None, {
            'fields' : (S.USER, S.TITLE, S.POST_CODE, S.POSTAL_ADDRESS, S.LATITUDE, S.LONGITUDE, S.CITY, S.STATE, S.IS_DEFAULT)
        }),
    )


@admin.register(UserRandomNumber)
class UserRandomNumberAdmin(admin.ModelAdmin):
    list_display = [S.USER, S.NUMBER, S.IS_ACTIVE]
    search_fields = [S.USER]

    fieldsets = (
        (None, {
            'fields' : (S.USER, S.NUMBER, S.IS_ACTIVE)
        }),
    )


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = [S.USER, S.TOTAL_AMOUNT]
    search_fields = [S.USER]
    list_filter = [S.TOTAL_AMOUNT]

    fieldsets =(
        (None, {
            'fields' : (S.USER, S.TOTAL_AMOUNT),
        }),
    )
    

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = [S.CART, S.PRODUCT_INSTANCE, S.COUNT]
    search_fields = [S.PRODUCT_INSTANCE, S.CART]
    list_filter = [S.COUNT, S.TOTAL_AMOUNT]

    fieldsets = (
        (None, {
            "fields": (
                S.CART, S.PRODUCT_INSTANCE, S.COUNT, S.TOTAL_AMOUNT
            ),
        }),
    )
    