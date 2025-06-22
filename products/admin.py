from django.contrib import admin

from .models import *

from utils.default_string import S


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [S.NAME, S.GENDER, ]
    list_filter = [S.GENDER,]
    search_fields = [S.NAME,]

    fieldsets = (
        (None, {
                'fields': (S.NAME, S.GENDER, S.COLORS, S.MATERIALS),
            }),
    )


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = [S.NAME, S.COLOR]
    search_fields = [S.NAME]


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = [S.NAME]
    search_fields = [S.NAME]


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = [S.NAME]
    search_fields = [S.NAME]


class AlbumInline (admin.TabularInline):
    model = ProductAlbum
    extra = 1
    fields = [S.FILE]


class ProductInstaceInline (admin.TabularInline):
    model = ProductInstance
    extra = 1
    fields = [S.PRODUCT, S.SIZE, S.COLOR, S.STOCK, S.P_ID]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [S.NAME, S.CATEGORY, S.RATE, S.PRICE, S.MATERIAL, 'in_stock']
    search_fields = [S.NAME, S.CATEGORY]
    list_filter = [S.CATEGORY, S.PRICE, S.RATE]

    inlines = [ProductInstaceInline, AlbumInline]

    def in_stock(self, obj):
        for instance in obj.instances.all():
            if instance.stock>0:
                return "Yes"
        return "No"
    
    fieldsets = (
        (None, {
            'fields': (S.NAME, S.CATEGORY, S.RATE, S.PRICE, S.MATERIAL, S.DESCRIPTION, S.IMAGE)
        }),
    )


@admin.register(ProductInstance)
class ProductInstanceAdmin (admin.ModelAdmin):
    list_display = [S.PRODUCT, S.STOCK, S.COLOR, S.SIZE, S.P_ID]
    search_fields = [S.PRODUCT, S.COLOR, S.P_ID]
    list_filter = [S.STOCK, S.SIZE]

    fieldsets = (
        (None, {
            'fields': (S.PRODUCT, S.STOCK, S.SIZE, S.COLOR, S.P_ID)
        }),
    )


@admin.register(ProductAlbum)
class ProductAlbumAdmin (admin.ModelAdmin):
    list_display = [S.PRODUCT]
    search_fields = [S.PRODUCT]

    fieldsets = (
        (None, {
            'fields': (S.PRODUCT, S.FILE)
        }),
    )