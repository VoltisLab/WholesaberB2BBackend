import graphene
from django.contrib.auth import get_user_model
from django.db.models import Q, Count, Avg
from products.models import Product, Category, Brand, Size
from accounts.models import User
from orders.models import Order, OrderItem
from reviews.models import Review
from graphql_jwt.decorators import login_required
from graphene import relay

User = get_user_model()


class ShopStatsType(graphene.ObjectType):
    """Shop statistics type"""
    total_products = graphene.Int()
    total_orders = graphene.Int()
    total_revenue = graphene.Float()
    average_rating = graphene.Float()
    total_reviews = graphene.Int()
    products_sold = graphene.Int()


class ShopProductType(graphene.ObjectType):
    """Shop product type with additional shop-specific fields"""
    id = graphene.ID()
    name = graphene.String()
    description = graphene.String()
    price = graphene.Float()
    images_url = graphene.JSONString()
    category = graphene.Field('products.schema.types.product_types.CategoryType')
    brand = graphene.Field('products.schema.types.product_types.BrandType')
    size = graphene.Field('products.schema.types.product_types.SizeType')
    seller = graphene.Field('accounts.schema.types.accounts_type.UserType')
    materials = graphene.List('products.schema.types.product_types.BrandType')
    user_liked = graphene.Boolean()
    created_at = graphene.DateTime()
    updated_at = graphene.DateTime()
    # Shop-specific fields
    total_sales = graphene.Int()
    total_revenue = graphene.Float()
    average_rating = graphene.Float()
    review_count = graphene.Int()


class GetShopData(graphene.Mutation):
    """Get shop data for a supplier"""
    class Arguments:
        seller_id = graphene.ID(required=False, description="Seller ID (defaults to current user)")
    
    success = graphene.Boolean()
    message = graphene.String()
    shop_stats = graphene.Field(ShopStatsType)
    products = graphene.List(ShopProductType)
    
    @login_required
    def mutate(self, info, **kwargs):
        try:
            user = info.context.user
            
            # Get seller ID (default to current user if not provided)
            seller_id = kwargs.get('seller_id')
            if seller_id:
                try:
                    seller = User.objects.get(id=seller_id)
                except User.DoesNotExist:
                    return GetShopData(
                        success=False,
                        message="Seller not found",
                        shop_stats=None,
                        products=[]
                    )
            else:
                seller = user
            
            # Calculate shop statistics
            products = Product.objects.filter(seller=seller)
            orders = Order.objects.filter(
                items__product__seller=seller
            ).distinct()
            
            # Calculate total products
            total_products = products.count()
            
            # Calculate total orders
            total_orders = orders.count()
            
            # Calculate total revenue
            total_revenue = sum(order.total_amount for order in orders)
            
            # Calculate products sold
            order_items = OrderItem.objects.filter(product__seller=seller)
            products_sold = sum(item.quantity for item in order_items)
            
            # Calculate average rating and total reviews
            reviews = Review.objects.filter(product__seller=seller)
            total_reviews = reviews.count()
            average_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0.0
            
            shop_stats = ShopStatsType(
                total_products=total_products,
                total_orders=total_orders,
                total_revenue=total_revenue,
                average_rating=round(average_rating, 2),
                total_reviews=total_reviews,
                products_sold=products_sold
            )
            
            # Get products with shop-specific data
            shop_products = []
            for product in products:
                # Calculate product-specific stats
                product_orders = OrderItem.objects.filter(product=product)
                product_total_sales = sum(item.quantity for item in product_orders)
                product_total_revenue = sum(item.quantity * item.price for item in product_orders)
                
                # Calculate product rating
                product_reviews = Review.objects.filter(product=product)
                product_review_count = product_reviews.count()
                product_average_rating = product_reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0.0
                
                shop_product = ShopProductType(
                    id=product.id,
                    name=product.name,
                    description=product.description,
                    price=product.price,
                    images_url=product.images_url,
                    category=product.category,
                    brand=product.brand,
                    size=product.size,
                    seller=product.seller,
                    materials=product.materials.all(),
                    user_liked=False,  # TODO: Implement user-specific like status
                    created_at=product.created_at,
                    updated_at=product.updated_at,
                    total_sales=product_total_sales,
                    total_revenue=product_total_revenue,
                    average_rating=round(product_average_rating, 2),
                    review_count=product_review_count
                )
                shop_products.append(shop_product)
            
            return GetShopData(
                success=True,
                message="Shop data retrieved successfully",
                shop_stats=shop_stats,
                products=shop_products
            )
            
        except Exception as e:
            return GetShopData(
                success=False,
                message=f"Error retrieving shop data: {str(e)}",
                shop_stats=None,
                products=[]
            )


class UpdateShopSettings(graphene.Mutation):
    """Update shop settings for a supplier"""
    class Arguments:
        shop_name = graphene.String(description="Shop name")
        shop_description = graphene.String(description="Shop description")
        shop_logo_url = graphene.String(description="Shop logo URL")
        shop_banner_url = graphene.String(description="Shop banner URL")
        shop_contact_email = graphene.String(description="Shop contact email")
        shop_contact_phone = graphene.String(description="Shop contact phone")
        shop_address = graphene.String(description="Shop address")
        shop_city = graphene.String(description="Shop city")
        shop_country = graphene.String(description="Shop country")
        shop_postal_code = graphene.String(description="Shop postal code")
    
    success = graphene.Boolean()
    message = graphene.String()
    shop_data = graphene.Field('accounts.schema.types.accounts_type.UserType')
    
    @login_required
    def mutate(self, info, **kwargs):
        try:
            user = info.context.user
            
            # Update user profile with shop information
            # For now, we'll store shop data in user profile fields
            # In a real implementation, you might want a separate Shop model
            
            if 'shop_name' in kwargs and kwargs['shop_name']:
                user.first_name = kwargs['shop_name']  # Using first_name as shop name for now
            
            if 'shop_description' in kwargs and kwargs['shop_description']:
                # Store in a custom field or user model extension
                pass
            
            if 'shop_contact_email' in kwargs and kwargs['shop_contact_email']:
                user.email = kwargs['shop_contact_email']
            
            if 'shop_contact_phone' in kwargs and kwargs['shop_contact_phone']:
                user.phone_number = kwargs['shop_contact_phone']
            
            if 'shop_address' in kwargs and kwargs['shop_address']:
                user.street_address = kwargs['shop_address']
            
            if 'shop_city' in kwargs and kwargs['shop_city']:
                user.city = kwargs['shop_city']
            
            if 'shop_country' in kwargs and kwargs['shop_country']:
                user.country = kwargs['shop_country']
            
            if 'shop_postal_code' in kwargs and kwargs['shop_postal_code']:
                user.postal_code = kwargs['shop_postal_code']
            
            user.save()
            
            return UpdateShopSettings(
                success=True,
                message="Shop settings updated successfully",
                shop_data=user
            )
            
        except Exception as e:
            return UpdateShopSettings(
                success=False,
                message=f"Error updating shop settings: {str(e)}",
                shop_data=None
            )


class ShopMutations(graphene.ObjectType):
    """Shop-related mutations"""
    get_shop_data = GetShopData.Field(description="Get shop data and statistics")
    update_shop_settings = UpdateShopSettings.Field(description="Update shop settings")

