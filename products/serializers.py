from rest_framework import serializers
from drf_yasg.utils import swagger_serializer_method

from django.db.models import Min, Max, Count

from .models import *

from utils.default_string import S


class ProductAlbumSeializer (serializers.ModelSerializer):
    """
        Serializer Model for product Album
    """

    class Meta:
        model = ProductAlbum
        fields = [S.ID, S.PRODUCT, S.FILE]


class CategoryFilterSerializer (serializers.ModelSerializer):
    price_range = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [S.COLORS, S.MATERIALS, 'price_range']

    def get_price_range(self, obj):
        products = Product.objects.filter(category=obj)
        if products.exists():
            price_range = products.aggregate(Min('price'), Max('price'))
            return {
                'min_price': price_range.get('price__min',0),
                'max_price': price_range.get('price__max',0)
            }
        return {'min_price':0, 'max_price':0}

class ColorSerializer (serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = [S.NAME, S.COLOR]


class MaterialSerializer (serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = [S.NAME]


class SizeSerializer (serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = [S.NAME]


class ProductInstanceSerializer (serializers.ModelSerializer):
    color = ColorSerializer()
    size = SizeSerializer()

    
    class Meta:
        model = ProductInstance
        fields = [S.ID, S.STOCK, S.COLOR, S.SIZE]


class ProductSerializer (serializers.ModelSerializer):
    material = MaterialSerializer()

    class Meta:
        model = Product
        fields = [S.ID, S.NAME, S.PRICE, S.CATEGORY, S.RATE, S.IMAGE, S.MATERIAL]


class ProductDetailSerializer (serializers.ModelSerializer):
    """
        Serializer for single product detailed view
    """
    material = MaterialSerializer()
    album = ProductAlbumSeializer(many=True, read_only=True)
    instances = ProductInstanceSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [S.ID, S.NAME, S.PRICE, S.CATEGORY, S.DESCRIPTION, S.RATE, S.IMAGE, S.MATERIAL, S.ALBUM, 'instances']

class CategorySerializer (serializers.ModelSerializer):
    """
        Serializer Model for All categories
    """
    products = ProductSerializer(many=True, read_only=True)
    class Meta:
        model = Category
        fields = [S.ID, S.NAME, S.GENDER, S.COLORS, S.MATERIALS, 'products']