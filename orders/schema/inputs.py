import graphene
from orders.models import Order, OrderItem, Payment, Cart, CartItem, Wishlist


class OrderInput(graphene.InputObjectType):
    shipping_address = graphene.JSONString(required=True)
    billing_address = graphene.JSONString(required=True)
    payment_method = graphene.String()
    notes = graphene.String()


class OrderItemInput(graphene.InputObjectType):
    product_id = graphene.ID(required=True)
    quantity = graphene.Int(required=True)


class PaymentInput(graphene.InputObjectType):
    payment_method = graphene.String(required=True)
    amount = graphene.Decimal(required=True)
    currency = graphene.String(default_value="USD")
    transaction_id = graphene.String()


class CartItemInput(graphene.InputObjectType):
    product_id = graphene.ID(required=True)
    quantity = graphene.Int(default_value=1)


class WishlistInput(graphene.InputObjectType):
    product_id = graphene.ID(required=True)
