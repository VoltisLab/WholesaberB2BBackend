from django.db import models
from django.utils import timezone
from accounts.models import User
from products.models import Product
from orders.models import Order

NULL = {"null": True, "blank": True}


class CustomerAnalytics(models.Model):
    """Analytics data for customers"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_analytics')
    
    # Order statistics
    total_orders = models.PositiveIntegerField(default=0)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Product statistics
    total_products_viewed = models.PositiveIntegerField(default=0)
    total_products_purchased = models.PositiveIntegerField(default=0)
    total_products_wishlisted = models.PositiveIntegerField(default=0)
    
    # Review statistics
    total_reviews_given = models.PositiveIntegerField(default=0)
    average_rating_given = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    
    # Activity statistics
    total_logins = models.PositiveIntegerField(default=0)
    last_login = models.DateTimeField(**NULL)
    days_since_last_order = models.PositiveIntegerField(**NULL)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Analytics for {self.user.email}"
    
    def update_analytics(self):
        """Update all analytics data for this customer"""
        # Order statistics
        orders = Order.objects.filter(customer=self.user)
        self.total_orders = orders.count()
        self.total_spent = sum(order.total_amount for order in orders)
        self.average_order_value = self.total_spent / self.total_orders if self.total_orders > 0 else 0
        
        # Product statistics
        self.total_products_viewed = ProductView.objects.filter(viewed_by=self.user).count()
        self.total_products_purchased = sum(
            order.items.count() for order in orders
        )
        self.total_products_wishlisted = Wishlist.objects.filter(user=self.user).count()
        
        # Review statistics
        reviews = Review.objects.filter(user=self.user)
        self.total_reviews_given = reviews.count()
        if reviews.exists():
            self.average_rating_given = sum(review.rating for review in reviews) / reviews.count()
        
        # Activity statistics
        self.last_login = self.user.last_login
        if self.user.last_login:
            self.days_since_last_order = (timezone.now() - self.user.last_login).days
        
        self.save()


class VendorAnalytics(models.Model):
    """Analytics data for vendors"""
    
    vendor = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendor_analytics')
    
    # Sales statistics
    total_products = models.PositiveIntegerField(default=0)
    total_orders = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Product performance
    total_views = models.PositiveIntegerField(default=0)
    total_likes = models.PositiveIntegerField(default=0)
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Review statistics
    total_reviews = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    five_star_reviews = models.PositiveIntegerField(default=0)
    four_star_reviews = models.PositiveIntegerField(default=0)
    three_star_reviews = models.PositiveIntegerField(default=0)
    two_star_reviews = models.PositiveIntegerField(default=0)
    one_star_reviews = models.PositiveIntegerField(default=0)
    
    # Customer statistics
    total_customers = models.PositiveIntegerField(default=0)
    returning_customers = models.PositiveIntegerField(default=0)
    new_customers = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Analytics for vendor {self.vendor.email}"
    
    def update_analytics(self):
        """Update all analytics data for this vendor"""
        # Sales statistics
        products = Product.objects.filter(seller=self.vendor)
        self.total_products = products.count()
        
        orders = Order.objects.filter(items__product__seller=self.vendor).distinct()
        self.total_orders = orders.count()
        
        # Calculate revenue and profit
        total_revenue = 0
        for order in orders:
            for item in order.items.filter(product__seller=self.vendor):
                total_revenue += item.total_price
        
        self.total_revenue = total_revenue
        self.average_order_value = total_revenue / self.total_orders if self.total_orders > 0 else 0
        
        # Product performance
        self.total_views = sum(product.views for product in products)
        self.total_likes = sum(product.likes for product in products)
        
        # Conversion rate calculation
        if self.total_views > 0:
            self.conversion_rate = (self.total_orders / self.total_views) * 100
        
        # Review statistics
        reviews = Review.objects.filter(product__seller=self.vendor)
        self.total_reviews = reviews.count()
        
        if reviews.exists():
            self.average_rating = sum(review.rating for review in reviews) / reviews.count()
            self.five_star_reviews = reviews.filter(rating=5).count()
            self.four_star_reviews = reviews.filter(rating=4).count()
            self.three_star_reviews = reviews.filter(rating=3).count()
            self.two_star_reviews = reviews.filter(rating=2).count()
            self.one_star_reviews = reviews.filter(rating=1).count()
        
        # Customer statistics
        customers = User.objects.filter(orders__items__product__seller=self.vendor).distinct()
        self.total_customers = customers.count()
        
        # Calculate returning vs new customers (simplified)
        self.returning_customers = customers.filter(orders__count__gt=1).count()
        self.new_customers = self.total_customers - self.returning_customers
        
        self.save()


class SalesReport(models.Model):
    """Sales reports for different time periods"""
    
    REPORT_TYPES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales_reports')
    report_type = models.CharField(max_length=10, choices=REPORT_TYPES)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    # Sales data
    total_orders = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_products_sold = models.PositiveIntegerField(default=0)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Growth metrics
    revenue_growth = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    order_growth = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['vendor', 'report_type', 'period_start', 'period_end']
        ordering = ['-period_end']
    
    def __str__(self):
        return f"Sales Report - {self.vendor.email} - {self.report_type} - {self.period_start.date()}"


class ProductAnalytics(models.Model):
    """Analytics for individual products"""
    
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='analytics')
    
    # View statistics
    total_views = models.PositiveIntegerField(default=0)
    unique_views = models.PositiveIntegerField(default=0)
    views_today = models.PositiveIntegerField(default=0)
    views_this_week = models.PositiveIntegerField(default=0)
    views_this_month = models.PositiveIntegerField(default=0)
    
    # Engagement statistics
    total_likes = models.PositiveIntegerField(default=0)
    total_wishlists = models.PositiveIntegerField(default=0)
    total_shares = models.PositiveIntegerField(default=0)
    
    # Sales statistics
    total_orders = models.PositiveIntegerField(default=0)
    total_quantity_sold = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Review statistics
    total_reviews = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Analytics for {self.product.name}"
    
    def update_analytics(self):
        """Update analytics for this product"""
        # View statistics
        self.total_views = self.product.views
        self.total_likes = self.product.likes
        
        # Wishlist count
        self.total_wishlists = Wishlist.objects.filter(product=self.product).count()
        
        # Sales statistics
        order_items = OrderItem.objects.filter(product=self.product)
        self.total_orders = order_items.count()
        self.total_quantity_sold = sum(item.quantity for item in order_items)
        self.total_revenue = sum(item.total_price for item in order_items)
        
        # Conversion rate
        if self.total_views > 0:
            self.conversion_rate = (self.total_orders / self.total_views) * 100
        
        # Review statistics
        reviews = Review.objects.filter(product=self.product)
        self.total_reviews = reviews.count()
        if reviews.exists():
            self.average_rating = sum(review.rating for review in reviews) / reviews.count()
        
        self.save()


# Import the models that are referenced
from products.models import ProductView
from orders.models import Wishlist
from reviews.models import Review
