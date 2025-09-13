from django.db import models
from accounts.models import User
from products.models import Product
from orders.models import Order

NULL = {"null": True, "blank": True}


class Review(models.Model):
    """Product reviews by customers"""
    
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    # Basic information
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='reviews', **NULL)
    
    # Review content
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    title = models.CharField(max_length=200, **NULL)
    comment = models.TextField(**NULL)
    
    # Review images
    images = models.JSONField(default=list, **NULL)
    
    # Review status
    is_verified_purchase = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    is_helpful = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['product', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.product.name} ({self.rating} stars)"
    
    def save(self, *args, **kwargs):
        # Check if this is a verified purchase
        if self.order and self.order.customer == self.user and self.order.status == 'delivered':
            self.is_verified_purchase = True
        super().save(*args, **kwargs)


class ReviewHelpful(models.Model):
    """Track which reviews users found helpful"""
    
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='helpful_votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='helpful_votes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['review', 'user']
    
    def __str__(self):
        return f"{self.user.email} found review helpful"


class ReviewResponse(models.Model):
    """Vendor responses to customer reviews"""
    
    review = models.OneToOneField(Review, on_delete=models.CASCADE, related_name='response')
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_responses')
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Response to review by {self.review.user.email}"


class ProductRating(models.Model):
    """Overall product rating aggregation"""
    
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='rating_summary')
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.PositiveIntegerField(default=0)
    rating_1_count = models.PositiveIntegerField(default=0)
    rating_2_count = models.PositiveIntegerField(default=0)
    rating_3_count = models.PositiveIntegerField(default=0)
    rating_4_count = models.PositiveIntegerField(default=0)
    rating_5_count = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.product.name} - {self.average_rating} stars ({self.total_reviews} reviews)"
    
    def update_rating(self):
        """Update rating statistics based on reviews"""
        reviews = self.product.reviews.filter(is_approved=True)
        total_reviews = reviews.count()
        
        if total_reviews > 0:
            total_rating = sum(review.rating for review in reviews)
            self.average_rating = round(total_rating / total_reviews, 2)
            self.total_reviews = total_reviews
            
            # Count ratings by star
            self.rating_1_count = reviews.filter(rating=1).count()
            self.rating_2_count = reviews.filter(rating=2).count()
            self.rating_3_count = reviews.filter(rating=3).count()
            self.rating_4_count = reviews.filter(rating=4).count()
            self.rating_5_count = reviews.filter(rating=5).count()
        else:
            self.average_rating = 0.00
            self.total_reviews = 0
            self.rating_1_count = 0
            self.rating_2_count = 0
            self.rating_3_count = 0
            self.rating_4_count = 0
            self.rating_5_count = 0
        
        self.save()


class VendorRating(models.Model):
    """Overall vendor rating aggregation"""
    
    vendor = models.OneToOneField(User, on_delete=models.CASCADE, related_name='rating_summary')
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.vendor.email} - {self.average_rating} stars ({self.total_reviews} reviews)"
    
    def update_rating(self):
        """Update vendor rating based on product reviews"""
        # Get all reviews for products sold by this vendor
        reviews = Review.objects.filter(
            product__seller=self.vendor,
            is_approved=True
        )
        
        total_reviews = reviews.count()
        
        if total_reviews > 0:
            total_rating = sum(review.rating for review in reviews)
            self.average_rating = round(total_rating / total_reviews, 2)
            self.total_reviews = total_reviews
        else:
            self.average_rating = 0.00
            self.total_reviews = 0
        
        self.save()
