from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
import random
import uuid
from faker import Faker

from accounts.models import User, VendorProfile, DeliveryAddress, PaymentMethod, NotificationPreference
from products.models import Category, Product, Brand, Material, Size
from orders.models import Order, OrderItem, Cart, CartItem, Wishlist, Payment

fake = Faker()

class Command(BaseCommand):
    help = 'Seed the database with fake data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=50,
            help='Number of users to create (default: 50)'
        )
        parser.add_argument(
            '--vendors',
            type=int,
            default=20,
            help='Number of vendors to create (default: 20)'
        )
        parser.add_argument(
            '--products',
            type=int,
            default=200,
            help='Number of products to create (default: 200)'
        )
        parser.add_argument(
            '--orders',
            type=int,
            default=100,
            help='Number of orders to create (default: 100)'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🌱 Starting database seeding...'))
        
        with transaction.atomic():
            # Create categories first
            self.create_categories()
            
            # Create brands and materials
            self.create_brands_and_materials()
            
            # Create sizes
            self.create_sizes()
            
            # Create users
            users = self.create_users(options['users'])
            
            # Create vendors
            vendors = self.create_vendors(options['vendors'], users)
            
            # Create products
            products = self.create_products(options['products'], vendors)
            
            # Create orders
            self.create_orders(options['orders'], users, products)
            
            # Create carts and wishlists
            self.create_carts_and_wishlists(users, products)
            
            # Create addresses and payment methods
            self.create_user_data(users)

        self.stdout.write(self.style.SUCCESS('✅ Database seeding completed successfully!'))

    def create_categories(self):
        """Create product categories"""
        self.stdout.write('Creating categories...')
        
        categories_data = [
            {'name': 'Fashion', 'slug': 'fashion'},
            {'name': 'Electronics', 'slug': 'electronics'},
            {'name': 'Home & Garden', 'slug': 'home-garden'},
            {'name': 'Sports & Outdoors', 'slug': 'sports-outdoors'},
            {'name': 'Beauty & Health', 'slug': 'beauty-health'},
            {'name': 'Books & Media', 'slug': 'books-media'},
            {'name': 'Toys & Games', 'slug': 'toys-games'},
            {'name': 'Automotive', 'slug': 'automotive'},
            {'name': 'Jewelry & Accessories', 'slug': 'jewelry-accessories'},
            {'name': 'Food & Beverages', 'slug': 'food-beverages'},
        ]
        
        for cat_data in categories_data:
            Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={'name': cat_data['name']}
            )

    def create_brands_and_materials(self):
        """Create brands and materials"""
        self.stdout.write('Creating brands and materials...')
        
        brands = [
            'Nike', 'Adidas', 'Apple', 'Samsung', 'Sony', 'Microsoft', 'Google',
            'Amazon', 'Tesla', 'BMW', 'Mercedes', 'Toyota', 'Honda', 'Ford',
            'Coca-Cola', 'Pepsi', 'McDonald\'s', 'Starbucks', 'Nike', 'Puma',
            'Reebok', 'Under Armour', 'New Balance', 'Converse', 'Vans'
        ]
        
        for brand_name in brands:
            Brand.objects.get_or_create(name=brand_name)
        
        materials = [
            'Cotton', 'Polyester', 'Leather', 'Denim', 'Silk', 'Wool', 'Linen',
            'Metal', 'Plastic', 'Wood', 'Glass', 'Ceramic', 'Rubber', 'Canvas',
            'Suede', 'Fur', 'Cashmere', 'Bamboo', 'Hemp', 'Lycra'
        ]
        
        for material_name in materials:
            Material.objects.get_or_create(name=material_name)

    def create_sizes(self):
        """Create product sizes"""
        self.stdout.write('Creating sizes...')
        
        size_data = [
            # Clothing sizes
            {'name': 'XS', 'size_type': 'clothing'},
            {'name': 'S', 'size_type': 'clothing'},
            {'name': 'M', 'size_type': 'clothing'},
            {'name': 'L', 'size_type': 'clothing'},
            {'name': 'XL', 'size_type': 'clothing'},
            {'name': 'XXL', 'size_type': 'clothing'},
            # Shoe sizes
            {'name': '6', 'size_type': 'shoes'},
            {'name': '7', 'size_type': 'shoes'},
            {'name': '8', 'size_type': 'shoes'},
            {'name': '9', 'size_type': 'shoes'},
            {'name': '10', 'size_type': 'shoes'},
            {'name': '11', 'size_type': 'shoes'},
            {'name': '12', 'size_type': 'shoes'},
            # General sizes
            {'name': 'Small', 'size_type': 'general'},
            {'name': 'Medium', 'size_type': 'general'},
            {'name': 'Large', 'size_type': 'general'},
        ]
        
        for size_info in size_data:
            Size.objects.get_or_create(
                name=size_info['name'],
                size_type=size_info['size_type']
            )

    def create_users(self, count):
        """Create fake users"""
        self.stdout.write(f'Creating {count} users...')
        
        users = []
        for i in range(count):
            user = User.objects.create(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.unique.email(),
                username=fake.unique.user_name(),
                phone_number=fake.phone_number(),
                city=fake.city(),
                street_address=fake.street_address(),
                postal_code=fake.postcode(),
                account_type='CUSTOMER' if i < count * 0.8 else 'VENDOR',
                is_verified=True,
                email_verified=True,
                terms_accepted=True,
                bio=fake.text(max_nb_chars=200),
                website=fake.url(),
                language_preference='en',
                timezone='UTC'
            )
            users.append(user)
            
            # Create notification preferences
            NotificationPreference.objects.create(
                user=user,
                push_notifications=True,
                push_orders=True,
                push_promotions=random.choice([True, False]),
                push_messages=True,
                push_reviews=True,
                email_notifications=random.choice([True, False]),
                email_orders=True,
                email_promotions=False,
                email_messages=False,
                email_reviews=True,
                email_newsletter=random.choice([True, False])
            )
        
        return users

    def create_vendors(self, count, users):
        """Create vendor profiles"""
        self.stdout.write(f'Creating {count} vendors...')
        
        vendor_users = [user for user in users if user.account_type == 'VENDOR']
        vendors = []
        
        for i, user in enumerate(vendor_users[:count]):
            vendor_profile = VendorProfile.objects.create(
                user=user,
                business_name=fake.company(),
                business_description=fake.text(max_nb_chars=500),
                business_phone=fake.phone_number(),
                business_email=fake.email(),
                business_website=fake.url(),
                business_address=fake.street_address(),
                business_city=fake.city(),
                business_state=fake.state(),
                business_country=fake.country(),
                business_postal_code=fake.postcode(),
                tax_id=fake.unique.numerify('##-#######'),
                business_license=fake.unique.alphanumeric(10),
                business_categories=random.sample([
                    'Fashion', 'Electronics', 'Home & Garden', 'Sports & Outdoors',
                    'Beauty & Health', 'Books & Media', 'Toys & Games', 'Automotive'
                ], random.randint(1, 3)),
                is_verified=random.choice([True, False]),
                total_products=0,
                total_sales=Decimal('0.00'),
                average_rating=Decimal(str(round(random.uniform(3.0, 5.0), 2)))
            )
            vendors.append(vendor_profile)
        
        return vendors

    def create_products(self, count, vendors):
        """Create fake products"""
        self.stdout.write(f'Creating {count} products...')
        
        categories = list(Category.objects.all())
        brands = list(Brand.objects.all())
        materials = list(Material.objects.all())
        sizes = list(Size.objects.all())
        
        products = []
        
        for i in range(count):
            vendor = random.choice(vendors)
            category = random.choice(categories)
            brand = random.choice(brands)
            
            # Generate product data
            name = fake.catch_phrase()
            description = fake.text(max_nb_chars=500)
            price = Decimal(str(round(random.uniform(10.0, 1000.0), 2)))
            discount_price = Decimal(str(round(random.uniform(5.0, price * 0.8), 2))) if random.choice([True, False]) else None
            
            # Generate fake images
            images = [fake.image_url() for _ in range(random.randint(1, 5))]
            
            product = Product.objects.create(
                name=name,
                seller=vendor.user,
                description=description,
                category=category,
                size=random.choice(sizes),
                style=random.choice(['casual', 'formal', 'sporty', 'vintage', 'modern']),
                condition=random.choice(['new', 'like_new', 'good', 'fair', 'poor']),
                price=price,
                discount_price=discount_price,
                images_url=images,
                status='active',
                color=[fake.color_name() for _ in range(random.randint(1, 3))],
                brand=brand,
                hashtags=[fake.word() for _ in range(random.randint(3, 8))],
                is_featured=random.choice([True, False]),
                views=random.randint(0, 1000),
                likes=random.randint(0, 100)
            )
            
            # Add materials
            product.materials.set(random.sample(materials, random.randint(1, 3)))
            
            products.append(product)
            
            # Update vendor product count
            vendor.total_products += 1
            vendor.save()
        
        return products

    def create_orders(self, count, users, products):
        """Create fake orders"""
        self.stdout.write(f'Creating {count} orders...')
        
        customer_users = [user for user in users if user.account_type == 'CUSTOMER']
        
        for i in range(count):
            customer = random.choice(customer_users)
            order_products = random.sample(products, random.randint(1, 5))
            
            # Generate order number
            order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
            
            # Calculate totals
            subtotal = sum(product.price for product in order_products)
            tax_amount = subtotal * Decimal('0.08')  # 8% tax
            shipping_cost = Decimal(str(round(random.uniform(5.0, 25.0), 2)))
            discount_amount = Decimal(str(round(random.uniform(0.0, subtotal * 0.2), 2)))
            total_amount = subtotal + tax_amount + shipping_cost - discount_amount
            
            order = Order.objects.create(
                order_number=order_number,
                customer=customer,
                status=random.choice(['pending', 'confirmed', 'processing', 'shipped', 'delivered']),
                payment_status=random.choice(['pending', 'paid', 'failed']),
                subtotal=subtotal,
                tax_amount=tax_amount,
                shipping_cost=shipping_cost,
                discount_amount=discount_amount,
                total_amount=total_amount,
                shipping_address={
                    'name': fake.name(),
                    'street': fake.street_address(),
                    'city': fake.city(),
                    'state': fake.state(),
                    'postal_code': fake.postcode(),
                    'country': fake.country()
                },
                billing_address={
                    'name': fake.name(),
                    'street': fake.street_address(),
                    'city': fake.city(),
                    'state': fake.state(),
                    'postal_code': fake.postcode(),
                    'country': fake.country()
                },
                payment_method=random.choice(['credit_card', 'debit_card', 'paypal', 'stripe']),
                payment_reference=fake.unique.alphanumeric(12),
                notes=fake.text(max_nb_chars=200) if random.choice([True, False]) else None,
                tracking_number=fake.unique.alphanumeric(15) if random.choice([True, False]) else None
            )
            
            # Create order items
            for product in order_products:
                quantity = random.randint(1, 5)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=product.price,
                    total_price=product.price * quantity,
                    product_name=product.name,
                    product_sku=fake.unique.alphanumeric(10),
                    product_image=product.images_url[0] if product.images_url else None
                )
            
            # Create payment record
            Payment.objects.create(
                order=order,
                payment_method=order.payment_method,
                status=order.payment_status,
                amount=total_amount,
                currency='USD',
                transaction_id=fake.unique.alphanumeric(20),
                gateway_response={'status': 'success', 'transaction_id': fake.unique.alphanumeric(20)}
            )

    def create_carts_and_wishlists(self, users, products):
        """Create carts and wishlists for users"""
        self.stdout.write('Creating carts and wishlists...')
        
        customer_users = [user for user in users if user.account_type == 'CUSTOMER']
        
        for user in customer_users:
            # Create cart
            cart, created = Cart.objects.get_or_create(user=user)
            
            # Add random items to cart
            cart_products = random.sample(products, random.randint(0, 5))
            for product in cart_products:
                CartItem.objects.get_or_create(
                    cart=cart,
                    product=product,
                    defaults={'quantity': random.randint(1, 3)}
                )
            
            # Add random items to wishlist
            wishlist_products = random.sample(products, random.randint(0, 10))
            for product in wishlist_products:
                Wishlist.objects.get_or_create(
                    user=user,
                    product=product
                )

    def create_user_data(self, users):
        """Create addresses and payment methods for users"""
        self.stdout.write('Creating user addresses and payment methods...')
        
        for user in users:
            # Create delivery addresses
            for i in range(random.randint(1, 3)):
                DeliveryAddress.objects.create(
                    user=user,
                    address_type=random.choice(['home', 'work', 'other']),
                    name=fake.name(),
                    phone_number=fake.phone_number(),
                    street_address=fake.street_address(),
                    city=fake.city(),
                    state=fake.state(),
                    country=fake.country(),
                    postal_code=fake.postcode(),
                    is_default=(i == 0),
                    instructions=fake.text(max_nb_chars=100) if random.choice([True, False]) else None
                )
            
            # Create payment methods
            for i in range(random.randint(1, 2)):
                PaymentMethod.objects.create(
                    user=user,
                    payment_type=random.choice(['credit_card', 'debit_card', 'paypal']),
                    is_default=(i == 0),
                    card_last_four=fake.numerify('####'),
                    card_brand=random.choice(['visa', 'mastercard', 'amex']),
                    card_exp_month=fake.numerify('##'),
                    card_exp_year=fake.numerify('####'),
                    gateway_payment_method_id=fake.unique.alphanumeric(20),
                    gateway_customer_id=fake.unique.alphanumeric(20),
                    billing_address={
                        'name': fake.name(),
                        'street': fake.street_address(),
                        'city': fake.city(),
                        'state': fake.state(),
                        'postal_code': fake.postcode(),
                        'country': fake.country()
                    }
                )

