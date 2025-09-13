import graphene
from graphene_django import DjangoObjectType
from django.db.models import Q

from orders.models import Order, OrderItem, Payment, Cart, CartItem, Wishlist
from orders.schema.types import OrderType, OrderItemType, PaymentType, CartType, CartItemType, WishlistType


class OrderQueries(graphene.ObjectType):
    """Order-related queries"""
    
    # Order queries
    my_orders = graphene.List(OrderType, status=graphene.String())
    order_by_id = graphene.Field(OrderType, order_id=graphene.ID(required=True))
    order_items = graphene.List(OrderItemType, order_id=graphene.ID(required=True))
    
    # Cart queries
    my_cart = graphene.Field(CartType)
    cart_items = graphene.List(CartItemType)
    
    # Wishlist queries
    my_wishlist = graphene.List(WishlistType)
    wishlist_count = graphene.Int()
    
    # Payment queries
    order_payment = graphene.Field(PaymentType, order_id=graphene.ID(required=True))
    
    def resolve_my_orders(self, info, status=None):
        """Get orders for the authenticated user"""
        user = info.context.user
        if not user.is_authenticated:
            return []
        
        queryset = Order.objects.filter(customer=user)
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-created_at')
    
    def resolve_order_by_id(self, info, order_id):
        """Get a specific order by ID"""
        user = info.context.user
        if not user.is_authenticated:
            return None
        
        try:
            return Order.objects.get(id=order_id, customer=user)
        except Order.DoesNotExist:
            return None
    
    def resolve_order_items(self, info, order_id):
        """Get items for a specific order"""
        user = info.context.user
        if not user.is_authenticated:
            return []
        
        try:
            order = Order.objects.get(id=order_id, customer=user)
            return order.items.all()
        except Order.DoesNotExist:
            return []
    
    def resolve_my_cart(self, info):
        """Get the user's cart"""
        user = info.context.user
        if not user.is_authenticated:
            return None
        
        cart, created = Cart.objects.get_or_create(user=user)
        return cart
    
    def resolve_cart_items(self, info):
        """Get items in the user's cart"""
        user = info.context.user
        if not user.is_authenticated:
            return []
        
        try:
            cart = Cart.objects.get(user=user)
            return cart.items.all()
        except Cart.DoesNotExist:
            return []
    
    def resolve_my_wishlist(self, info):
        """Get the user's wishlist"""
        user = info.context.user
        if not user.is_authenticated:
            return []
        
        return Wishlist.objects.filter(user=user).order_by('-created_at')
    
    def resolve_wishlist_count(self, info):
        """Get the number of items in the user's wishlist"""
        user = info.context.user
        if not user.is_authenticated:
            return 0
        
        return Wishlist.objects.filter(user=user).count()
    
    def resolve_order_payment(self, info, order_id):
        """Get payment information for an order"""
        user = info.context.user
        if not user.is_authenticated:
            return None
        
        try:
            order = Order.objects.get(id=order_id, customer=user)
            return order.payment
        except Order.DoesNotExist:
            return None
