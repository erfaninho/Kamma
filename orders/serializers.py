from rest_framework import serializers

from .models import Order, OrderItem, Payment

from products.models import ProductInstance

from users.models import Cart, CartItem, SessionCart, SessionCartItem
from users.serializers import address

from utils.default_string import S
from utils.serializers import BaseSerializer

class CartProductInstanceSerializer(serializers.ModelSerializer):
    """
        Serializer for showing product instances in cart
    """
    class Meta:
        model = ProductInstance
        fields = (S.PRODUCT, S.COLOR, S.SIZE)

class CartItemSerializer(serializers.ModelSerializer):
    """
        Serializer for cart items
    """
    product = CartProductInstanceSerializer()

    class Meta:
        model = CartItem
        fields = ("product", S.COUNT, S.TOTAL_AMOUNT)


class SessionCartItemSerializer(serializers.ModelSerializer):
    """
        Session Cart item Serializer To display
    """
    product = CartProductInstanceSerializer()

    class Meta:
        model = SessionCartItem
        fields = ("product", S.COUNT, S.TOTAL_AMOUNT)


class SessionCartSerializer(serializers.ModelSerializer):
    """
        Session cart serializer for not logged in users
    """
    items = SessionCartItemSerializer(many=True, read_only=True)

    class Meta:
        model = SessionCart
        fields = (S.SESSION, S.TOTAL_AMOUNT, "items")


class AddToCartSerializer(serializers.ModelSerializer):
    """
        Add to cart serializer
    """

    class Meta:
        model = CartItem
        fields = (S.PRODUCT_INSTANCE, S.COUNT)


class AddToSessionCartSerializer(serializers.ModelSerializer):
    """
        Add to cart serializer
    """

    class Meta:
        model = SessionCartItem
        fields = (S.PRODUCT_INSTANCE, S.COUNT)


class CartSerializer(serializers.ModelSerializer):
    """
        Serializer for cart
    """
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = (S.USER, S.TOTAL_AMOUNT, "items")


class OrderItemSerializer(serializers.ModelSerializer):
    """
        Serializer for Order Item
    """

    class Meta:
        model = OrderItem
        fields = (S.PRODUCT, S.COUNT, S.TOTAL_AMOUNT)

    
class OrderSerializer(serializers.ModelSerializer):
    """
        Serializer for order
    """
    items = OrderItemSerializer(many=True, read_only=True)
    address = address.OrderAddressSerializer()

    class Meta:
        model = Order
        fields = (S.USER, S.TOTAL_AMOUNT, 'items', 'address', S.ORDER_STATUS, S.NUMBER)


class UserOrdersSerializer (serializers.ModelSerializer):
    """
        Serializer to show all user orders summary
    """

    class Meta:
        model = Order
        fields = (S.NUMBER, S.ORDER_STATUS, S.TOTAL_AMOUNT, S.INSERT_DT)


class UserPayments (serializers.ModelSerializer):
    """
        Serializer To display all user payments
    """

    class Meta:
        model = Payment
        fields = (S.ORDER, S.USER, S.PAYMENT_STATUS)


class StartPaymentSerializer (BaseSerializer):

    @staticmethod
    def create_order(user, shipping_address):
        order = Order.objects.create(
            user=user,
            shipping_address=shipping_address
        )
        return order
    
    @staticmethod
    def create_payment(order, user):
        payment = Payment.objects.create(
            order=order,
            user=user
        )
        return payment
    

    def create(self, validated_data):
        user = self.context['request'].user
        address = user.addresses.last()
        order = self.create_order(user=user, shipping_address=address)
        payment = self.create_payment(order=order, user=user)
        return payment