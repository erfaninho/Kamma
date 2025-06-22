from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Category, Product, ProductInstance
from .filters import ProductFilter
from .serializers import ProductiInstanceSerializer, ProductSerializer, CatogorySerializer, MaterialSerializer, \
    SizeSerializer
from utils.default_string import T, S
from utils.views import RetrieveMixin #, PostMixin, DestroyMixin


class CategoryViewSet(viewsets.ReadOnlyModelViewSet, RetrieveMixin):
    """
        Get All Categories
    """
    queryset = Category.objects.all()
    permission_classes = [AllowAny]

    serializer_class = CatogorySerializer

    def get_queryset(self):
        return super().get_queryset()
    
    def get_filterset_class(self):
        return ProductFilter
    
    @swagger_auto_schema(
        operation_summary="Get All Categories",
        tags=[T.CATEGORY_TAG]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Get Details of one category",
        tags=[T.CATEGORY_TAG]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Get list of one category filters",
        tags=[T.CATEGORY_TAG]
    )
    @action(detail=True, methods=['get'])
    def filters(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Get filtered list of products of one category",
        tags=[T.CATEGORY_TAG]
    )
    @action(detail=True, methods=['get'])
    def products(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    permission_classes = [AllowAny]

    def get_queryset(self):
        if self.action == 'list':
            return Product.objects.all()
        if self.action == 'retrieve':
            return Product.objects.all()
        if self.action == 'search':
            return Product.objects.all()
    

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductSerializer
        if self.action == 'retrieve':
            return ProductSerializer 
        if self.action == 'search':
            return ProductSerializer
        
    def get_queryset(self):
        query = self.request.query_params.get("search")
        if query is not None:
            return Product.objects.filter(name__icontains=query)
        return super().get_queryset()
    
    @swagger_auto_schema(
        operation_summary="Get all Products List",
        tags=[T.PRODUCT_TAG]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Get Specific Product Detail",
        tags=[T.PRODUCT_TAG]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Search by Keyword",
        tags=[T.PRODUCT_TAG]
    )
    def serach(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)