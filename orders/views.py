from drf_yasg.utils import swagger_auto_schema

from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Order, OrderItem
from users.models import Cart, CartItem

from .serializers import *
from utils.views import PostMixin, RetrieveMixin

from utils.default_string import T
from utils.server_utils import token_generator


class CartViewSet(PostMixin, RetrieveMixin, viewsets.GenericViewSet, mixins.UpdateModelMixin):
    """
        Viewsets to add, remove, and update cart
    """
    serializer_class = CartSerializer
    def get_serializer_class(self, *args, **kwargs):
        if self.action in ["get_cart"]:
            if self.request.user.is_authenticated:
                return CartSerializer
            else:
                return SessionCartSerializer
        if self.action in ["update_cart_item", "remove_from_cart"]:
            if self.request.user.is_authenticated:
                return CartItemSerializer
            else:
                return SessionCartItemSerializer
        if self.action in ["add_to_cart"]:
            if self.request.user.is_authenticated:
                return AddToCartSerializer
            else:
                return AddToSessionCartSerializer
        return super().get_serializer_class()
    
    def get_or_create_cart(self):
        user = self.request.user
        if user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=user)
            return cart
        else:
            token = self.request.session.session_key
            session_cart, _ = SessionCart.objects.get_or_create(session=token)
            return session_cart
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Cart.objects.filter(user=self.request.user)
        else:
            return SessionCart.objects.filter(session=self.request.session.session_key)
    
    def get_object(self):
        if self.action in ["update_cart_item", "remove_from_cart"]:
            return self.get_or_create_cart().items.get(product=self.request.data.get("product"))
        if self.action in ["get_cart", "add_to_cart"]:
            return self.get_or_create_cart()
        return super().get_object()

    @swagger_auto_schema(
        operation_summary="Add to Cart",
        tags=[T.CART_TAG]
    )
    @action(detail=False, methods=['post'])
    def add_to_cart(self, request, *args, **kwargs):
        return self.custom_create(request)
    
    @swagger_auto_schema(
        operation_summary="Upadte Cart Item",
        tags=[T.CART_TAG]
    )
    @action(detail=False, methods=['post'])
    def update_cart_item(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Get Cart",
        tags=[T.CART_TAG]
    )
    @action(detail=False, methods=['get'])
    def get_cart(self, request, *args, **kwargs):
        return self.custom_retrieve(request, *args, **kwargs)


class CreatePaymnetViewSet(PostMixin, RetrieveMixin, viewsets.GenericViewSet):
    """
        Viewsets to create and show orders
    """
    serializer_class = StartPaymentSerializer
    
    @swagger_auto_schema(
        operation_summary="Start Payment",
        tags=['Payment']
    )
    @action(detail=False, methods=['post'])
    def create_payment(self, request, *args, **kwargs):
        return self.custom_create(request, *args, **kwargs)


# class SuccessfullPaymentVieset()