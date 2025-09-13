from django.contrib import admin
from .models import CustomerAnalytics, VendorAnalytics, SalesReport, ProductAnalytics


@admin.register(CustomerAnalytics)
class CustomerAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_orders', 'total_spent', 'average_order_value', 'updated_at']
    list_filter = ['updated_at']
    search_fields = ['user__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(VendorAnalytics)
class VendorAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'total_products', 'total_orders', 'total_revenue', 'average_rating', 'updated_at']
    list_filter = ['updated_at']
    search_fields = ['vendor__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(SalesReport)
class SalesReportAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'report_type', 'period_start', 'period_end', 'total_revenue', 'total_orders']
    list_filter = ['report_type', 'period_start', 'period_end']
    search_fields = ['vendor__email']
    readonly_fields = ['created_at']


@admin.register(ProductAnalytics)
class ProductAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['product', 'total_views', 'total_orders', 'total_revenue', 'average_rating', 'updated_at']
    list_filter = ['updated_at']
    search_fields = ['product__name']
    readonly_fields = ['created_at', 'updated_at']
