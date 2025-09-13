import graphene
from graphene_django import DjangoObjectType
from django.db.models import Q, Avg, Count

from reviews.models import Review, ReviewHelpful, ReviewResponse, ProductRating, VendorRating
from reviews.schema.types import ReviewType, ReviewHelpfulType, ReviewResponseType, ProductRatingType, VendorRatingType
from products.models import Product


class ReviewQueries(graphene.ObjectType):
    """Review-related queries"""
    
    # Review queries
    product_reviews = graphene.List(ReviewType, product_id=graphene.ID(required=True))
    my_reviews = graphene.List(ReviewType)
    review_by_id = graphene.Field(ReviewType, review_id=graphene.ID(required=True))
    
    # Rating queries
    product_rating = graphene.Field(ProductRatingType, product_id=graphene.ID(required=True))
    vendor_rating = graphene.Field(VendorRatingType, vendor_id=graphene.ID(required=True))
    
    # Review statistics
    review_stats = graphene.Field(graphene.JSONString, product_id=graphene.ID(required=True))
    
    def resolve_product_reviews(self, info, product_id):
        """Get reviews for a specific product"""
        try:
            product = Product.objects.get(id=product_id)
            return Review.objects.filter(
                product=product,
                is_approved=True
            ).order_by('-created_at')
        except Product.DoesNotExist:
            return []
    
    def resolve_my_reviews(self, info):
        """Get reviews by the authenticated user"""
        user = info.context.user
        if not user.is_authenticated:
            return []
        
        return Review.objects.filter(user=user).order_by('-created_at')
    
    def resolve_review_by_id(self, info, review_id):
        """Get a specific review by ID"""
        try:
            return Review.objects.get(id=review_id)
        except Review.DoesNotExist:
            return None
    
    def resolve_product_rating(self, info, product_id):
        """Get rating summary for a product"""
        try:
            product = Product.objects.get(id=product_id)
            rating, created = ProductRating.objects.get_or_create(product=product)
            if created:
                rating.update_rating()
            return rating
        except Product.DoesNotExist:
            return None
    
    def resolve_vendor_rating(self, info, vendor_id):
        """Get rating summary for a vendor"""
        try:
            from accounts.models import User
            vendor = User.objects.get(id=vendor_id)
            rating, created = VendorRating.objects.get_or_create(vendor=vendor)
            if created:
                rating.update_rating()
            return rating
        except User.DoesNotExist:
            return None
    
    def resolve_review_stats(self, info, product_id):
        """Get detailed review statistics for a product"""
        try:
            product = Product.objects.get(id=product_id)
            reviews = Review.objects.filter(product=product, is_approved=True)
            
            stats = {
                'total_reviews': reviews.count(),
                'average_rating': reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0,
                'rating_distribution': {
                    '5_star': reviews.filter(rating=5).count(),
                    '4_star': reviews.filter(rating=4).count(),
                    '3_star': reviews.filter(rating=3).count(),
                    '2_star': reviews.filter(rating=2).count(),
                    '1_star': reviews.filter(rating=1).count(),
                },
                'verified_purchases': reviews.filter(is_verified_purchase=True).count(),
                'with_images': reviews.exclude(images__isnull=True).exclude(images=[]).count(),
            }
            
            return stats
            
        except Product.DoesNotExist:
            return None
