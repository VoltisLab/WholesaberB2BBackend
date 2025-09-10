from django.contrib import admin
from accounts.models import User


admin.site.site_header = "Wholesalers Market Admin Panel"
admin.site.site_title = "Wholesalers Market Admin"
admin.site.index_title = "Welcome to Wholesalers Market Dashboard"


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "is_active",
        "account_type",
        "first_name",
        "last_name",
        "is_superuser",
    )
    search_fields = (
        "email",
        "account_type",
    )
