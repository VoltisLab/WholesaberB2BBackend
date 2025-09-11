from django.contrib import admin
from accounts.models import User, PhoneVerification, Verification


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

@admin.register(PhoneVerification)
class PhoneVerificationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "phone_number",
        "otp_code",
        "is_used",
        "created_at",
    )
    search_fields = (
        "user__email",
        "phone_number",
        "otp_code",
    )

@admin.register(Verification)
class VerificationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "code",
        "date_created",
    )
    search_fields = (
        "user__email",
        "code",
    )