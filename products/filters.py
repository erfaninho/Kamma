from django_filters import rest_framework as filters
from .models import Product

from utils.default_string import S


class ProductFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="price", lookup_expr='lte')
    colors = filters.BaseInFilter(field_name="color__id")
    materials = filters.BaseInFilter(field_name="material__id")
    has_stock = filters.BooleanFilter(method="filter_has_stock")

    class Meta:
        model = Product
        fields = [S.CATEGORY, S.COLORS, S.MATERIALS, 'min_price', 'max_price', 'has_stock']

    def filter_has_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock__gt=0)
        return queryset.filter(stock__lte=0)