import graphene
from graphql import GraphQLError
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
import uuid

from orders.models import Order, OrderItem, Payment, Cart, CartItem, Wishlist
from orders.schema.types import OrderType, OrderItemType, PaymentType, CartType, CartItemType, WishlistType
from orders.schema.inputs import OrderInput, OrderItemInput, PaymentInput, CartItemInput, WishlistInput
from products.models import Product


class CreateOrderMutation(graphene.Mutation):
    """Create a new order"""
    
    class Arguments:
        order_data = OrderInput(required=True)
        items = graphene.List(OrderItemInput, required=True)
    
    order = graphene.Field(OrderType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, order_data, items):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("Authentication required")
        
        try:
            with transaction.atomic():
                # Generate order number
                order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
                
                # Calculate totals
                subtotal = Decimal('0.00')
                order_items_data = []
                
                for item_data in items:
                    try:
                        product = Product.objects.get(id=item_data.product_id)
                        item_total = product.price * item_data.quantity
                        subtotal += item_total
                        
                        order_items_data.append({
                            'product': product,
                            'quantity': item_data.quantity,
                            'unit_price': product.price,
                            'total_price': item_total,
                        })
                    except Product.DoesNotExist:
                        raise GraphQLError(f"Product with ID {item_data.product_id} not found")
                
                # Calculate tax (simplified - 10% tax)
                tax_amount = subtotal * Decimal('0.10')
                shipping_cost = Decimal('10.00')  # Fixed shipping cost
                total_amount = subtotal + tax_amount + shipping_cost
                
                # Create order
                order = Order.objects.create(
                    order_number=order_number,
                    customer=user,
                    subtotal=subtotal,
                    tax_amount=tax_amount,
                    shipping_cost=shipping_cost,
                    total_amount=total_amount,
                    shipping_address=order_data.shipping_address,
                    billing_address=order_data.billing_address,
                    payment_method=order_data.payment_method,
                    notes=order_data.notes,
                )
                
                # Create order items
                for item_data in order_items_data:
                    OrderItem.objects.create(
                        order=order,
                        product=item_data['product'],
                        quantity=item_data['quantity'],
                        unit_price=item_data['unit_price'],
                        total_price=item_data['total_price'],
                    )
                
                return CreateOrderMutation(
                    order=order,
                    success=True,
                    message="Order created successfully"
                )
                
        except Exception as e:
            raise GraphQLError(f"Failed to create order: {str(e)}")


class AddToCartMutation(graphene.Mutation):
    """Add item to cart"""
    
    class Arguments:
        product_id = graphene.ID(required=True)
        quantity = graphene.Int(default_value=1)
    
    cart_item = graphene.Field(CartItemType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, product_id, quantity):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("Authentication required")
        
        try:
            product = Product.objects.get(id=product_id)
            
            # Get or create cart
            cart, created = Cart.objects.get_or_create(user=user)
            
            # Get or create cart item
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            return AddToCartMutation(
                cart_item=cart_item,
                success=True,
                message="Item added to cart successfully"
            )
            
        except Product.DoesNotExist:
            raise GraphQLError("Product not found")
        except Exception as e:
            raise GraphQLError(f"Failed to add item to cart: {str(e)}")


class UpdateCartItemMutation(graphene.Mutation):
    """Update cart item quantity"""
    
    class Arguments:
        cart_item_id = graphene.ID(required=True)
        quantity = graphene.Int(required=True)
    
    cart_item = graphene.Field(CartItemType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, cart_item_id, quantity):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("Authentication required")
        
        try:
            cart_item = CartItem.objects.get(id=cart_item_id, cart__user=user)
            
            if quantity <= 0:
                cart_item.delete()
                return UpdateCartItemMutation(
                    cart_item=None,
                    success=True,
                    message="Item removed from cart"
                )
            
            cart_item.quantity = quantity
            cart_item.save()
            
            return UpdateCartItemMutation(
                cart_item=cart_item,
                success=True,
                message="Cart item updated successfully"
            )
            
        except CartItem.DoesNotExist:
            raise GraphQLError("Cart item not found")
        except Exception as e:
            raise GraphQLError(f"Failed to update cart item: {str(e)}")


class RemoveFromCartMutation(graphene.Mutation):
    """Remove item from cart"""
    
    class Arguments:
        cart_item_id = graphene.ID(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, cart_item_id):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("Authentication required")
        
        try:
            cart_item = CartItem.objects.get(id=cart_item_id, cart__user=user)
            cart_item.delete()
            
            return RemoveFromCartMutation(
                success=True,
                message="Item removed from cart"
            )
            
        except CartItem.DoesNotExist:
            raise GraphQLError("Cart item not found")
        except Exception as e:
            raise GraphQLError(f"Failed to remove cart item: {str(e)}")


class AddToWishlistMutation(graphene.Mutation):
    """Add item to wishlist"""
    
    class Arguments:
        product_id = graphene.ID(required=True)
    
    wishlist_item = graphene.Field(WishlistType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, product_id):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("Authentication required")
        
        try:
            product = Product.objects.get(id=product_id)
            
            wishlist_item, created = Wishlist.objects.get_or_create(
                user=user,
                product=product
            )
            
            if not created:
                raise GraphQLError("Item already in wishlist")
            
            return AddToWishlistMutation(
                wishlist_item=wishlist_item,
                success=True,
                message="Item added to wishlist successfully"
            )
            
        except Product.DoesNotExist:
            raise GraphQLError("Product not found")
        except Exception as e:
            raise GraphQLError(f"Failed to add item to wishlist: {str(e)}")


class RemoveFromWishlistMutation(graphene.Mutation):
    """Remove item from wishlist"""
    
    class Arguments:
        product_id = graphene.ID(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, product_id):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("Authentication required")
        
        try:
            wishlist_item = Wishlist.objects.get(user=user, product_id=product_id)
            wishlist_item.delete()
            
            return RemoveFromWishlistMutation(
                success=True,
                message="Item removed from wishlist"
            )
            
        except Wishlist.DoesNotExist:
            raise GraphQLError("Item not found in wishlist")
        except Exception as e:
            raise GraphQLError(f"Failed to remove item from wishlist: {str(e)}")


class OrderMutations(graphene.ObjectType):
    create_order = CreateOrderMutation.Field()
    add_to_cart = AddToCartMutation.Field()
    update_cart_item = UpdateCartItemMutation.Field()
    remove_from_cart = RemoveFromCartMutation.Field()
    add_to_wishlist = AddToWishlistMutation.Field()
    remove_from_wishlist = RemoveFromWishlistMutation.Field()
