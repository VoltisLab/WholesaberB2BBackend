from django.contrib import admin
from .models import Review, ReviewHelpful, ReviewResponse, ProductRating, VendorRating


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'is_verified_purchase', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_verified_purchase', 'is_approved', 'created_at']
    search_fields = ['product__name', 'user__email', 'title']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(ReviewHelpful)
class ReviewHelpfulAdmin(admin.ModelAdmin):
    list_display = ['review', 'user', 'created_at']
    list_filter = ['created_at']


@admin.register(ReviewResponse)
class ReviewResponseAdmin(admin.ModelAdmin):
    list_display = ['review', 'vendor', 'created_at']
    list_filter = ['created_at']


@admin.register(ProductRating)
class ProductRatingAdmin(admin.ModelAdmin):
    list_display = ['product', 'average_rating', 'total_reviews', 'last_updated']
    list_filter = ['last_updated']
    search_fields = ['product__name']


@admin.register(VendorRating)
class VendorRatingAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'average_rating', 'total_reviews', 'last_updated']
    list_filter = ['last_updated']
    search_fields = ['vendor__email']
