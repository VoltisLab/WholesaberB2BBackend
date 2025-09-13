import graphene
from graphene_django import DjangoObjectType
from orders.models import Order, OrderItem, Payment, Cart, CartItem, Wishlist


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"


class OrderItemType(DjangoObjectType):
    class Meta:
        model = OrderItem
        fields = "__all__"


class PaymentType(DjangoObjectType):
    class Meta:
        model = Payment
        fields = "__all__"


class CartType(DjangoObjectType):
    class Meta:
        model = Cart
        fields = "__all__"


class CartItemType(DjangoObjectType):
    class Meta:
        model = CartItem
        fields = "__all__"


class WishlistType(DjangoObjectType):
    class Meta:
        model = Wishlist
        fields = "__all__"
