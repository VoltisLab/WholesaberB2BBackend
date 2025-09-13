from django.db import models

from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)

NULL = {"blank": True, "null": True}

from phonenumber_field.modelfields import PhoneNumberField
from accounts.choices import GenderChoice, AccountType
from django.utils import timezone


class UserManager(BaseUserManager):
    def create(self, username, **kwargs):
        # if username is None:
        #     raise ValueError("username can not be null")

        user = self.model(username=username, **kwargs)
        user.set_password(kwargs.get("password"))
        user.save(using=self._db)
        return user

    def create_superuser(self, username, **kwargs):
        kwargs["is_staff"] = True
        kwargs["is_superuser"] = True
        return self.create(username=username, **kwargs)

    def create_user(self, username, **kwargs):
        return self.create(username=username, **kwargs)


# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(
        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, **NULL)
    username = models.CharField(max_length=100, unique=True, **NULL)
    dob = models.DateField(**NULL)
    dob_change_count = models.IntegerField(default=0)
    email = models.EmailField(unique=True, **NULL)
    profile_picture_url = models.CharField(max_length=255, **NULL)
    thumbnail_url = models.URLField(blank=True, null=True)
    gender = models.CharField(max_length=25, choices=GenderChoice.choices, **NULL)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    display_name = models.CharField(max_length=100, **NULL)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    phone_number = PhoneNumberField(unique=True, **NULL)
    date_joined = models.DateTimeField(default=timezone.localtime, editable=False)
    account_type = models.CharField(
        max_length=25,
        choices=AccountType.choices,
        default=AccountType.CUSTOMER,
    )
    city = models.CharField(max_length=100, **NULL)
    street_address = models.CharField(max_length=255, **NULL)
    postal_code = models.CharField(max_length=20, **NULL)
    last_login = models.DateTimeField(**NULL)
    last_seen = models.DateTimeField(**NULL)
    meta = models.JSONField(default=dict, **NULL)
    terms_accepted = models.BooleanField(default=False)
    
    # Additional profile fields
    bio = models.TextField(**NULL)
    website = models.URLField(**NULL)
    social_links = models.JSONField(default=dict, **NULL)
    privacy_settings = models.JSONField(default=dict, **NULL)
    language_preference = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='UTC')

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    objects = UserManager()
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class PhoneVerification(models.Model):
    """Model for phone verification OTP"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="phone_verifications"
    )
    phone_number = models.CharField(max_length=20)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    attempts = models.PositiveIntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=["user", "is_used"]),
            models.Index(fields=["phone_number", "otp_code"]),
        ]

    def is_expired(self):
        return timezone.now() > self.expires_at

    def increment_attempts(self):
        self.attempts += 1
        self.save(update_fields=["attempts"])

    def __str__(self):
        return f"Phone verification for {self.user.email}"


class Verification(models.Model):
    user = models.OneToOneField(
        User, related_name="otp", unique=True, on_delete=models.CASCADE
    )
    code = models.CharField(max_length=10, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email


class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    # result_count = models.IntegerField(null=True, blank=True)
    search_type = models.CharField(max_length=100, null=True, blank=True)
    deleted = models.BooleanField(default=False)
    search_count = models.IntegerField(default=1)
    search_frequency = models.IntegerField(default=1)
    last_searched = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-timestamp"]


class DeliveryAddress(models.Model):
    ADDRESS_TYPES = [
        ('home', 'Home'),
        ('work', 'Work'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="delivery_addresses"
    )
    address_type = models.CharField(max_length=50, choices=ADDRESS_TYPES, default='home')
    name = models.CharField(max_length=100)
    phone_number = PhoneNumberField()
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, **NULL)
    country = models.CharField(max_length=100, default='United States')
    postal_code = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, **NULL)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, **NULL)
    instructions = models.TextField(**NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.name} - {self.get_address_type_display()}"
    
    def get_full_address(self):
        return f"{self.street_address}, {self.city}, {self.state} {self.postal_code}, {self.country}"


class PaymentMethod(models.Model):
    """User payment methods"""
    
    PAYMENT_TYPES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('paypal', 'PayPal'),
        ('apple_pay', 'Apple Pay'),
        ('google_pay', 'Google Pay'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    is_default = models.BooleanField(default=False)
    
    # Card information (encrypted)
    card_last_four = models.CharField(max_length=4, **NULL)
    card_brand = models.CharField(max_length=20, **NULL)  # visa, mastercard, etc.
    card_exp_month = models.CharField(max_length=2, **NULL)
    card_exp_year = models.CharField(max_length=4, **NULL)
    
    # Payment gateway information
    gateway_payment_method_id = models.CharField(max_length=100, **NULL)
    gateway_customer_id = models.CharField(max_length=100, **NULL)
    
    # Additional information
    billing_address = models.JSONField(default=dict, **NULL)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        if self.card_last_four:
            return f"{self.get_payment_type_display()} ending in {self.card_last_four}"
        return f"{self.get_payment_type_display()}"


class NotificationPreference(models.Model):
    """User notification preferences"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='account_notification_preferences')
    
    # Push notifications
    push_notifications = models.BooleanField(default=True)
    push_orders = models.BooleanField(default=True)
    push_promotions = models.BooleanField(default=False)
    push_messages = models.BooleanField(default=True)
    push_reviews = models.BooleanField(default=True)
    
    # Email notifications
    email_notifications = models.BooleanField(default=False)
    email_orders = models.BooleanField(default=True)
    email_promotions = models.BooleanField(default=False)
    email_messages = models.BooleanField(default=False)
    email_reviews = models.BooleanField(default=True)
    email_newsletter = models.BooleanField(default=False)
    
    # SMS notifications
    sms_notifications = models.BooleanField(default=False)
    sms_orders = models.BooleanField(default=True)
    sms_promotions = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Notification preferences for {self.user.email}"


class VendorProfile(models.Model):
    """Extended vendor profile information"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendor_profile')
    
    # Business information
    business_name = models.CharField(max_length=200)
    business_description = models.TextField(**NULL)
    business_phone = PhoneNumberField(**NULL)
    business_email = models.EmailField(**NULL)
    business_website = models.URLField(**NULL)
    
    # Business address
    business_address = models.CharField(max_length=255, **NULL)
    business_city = models.CharField(max_length=100, **NULL)
    business_state = models.CharField(max_length=100, **NULL)
    business_country = models.CharField(max_length=100, **NULL)
    business_postal_code = models.CharField(max_length=20, **NULL)
    
    # Business details
    tax_id = models.CharField(max_length=50, **NULL)
    business_license = models.CharField(max_length=100, **NULL)
    business_categories = models.JSONField(default=list, **NULL)
    
    # Verification status
    is_verified = models.BooleanField(default=False)
    verification_documents = models.JSONField(default=list, **NULL)
    verification_notes = models.TextField(**NULL)
    
    # Business metrics
    total_products = models.PositiveIntegerField(default=0)
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Vendor profile for {self.business_name}"


class SupportTicket(models.Model):
    """Support tickets for customer service"""
    
    TICKET_TYPES = [
        ('general', 'General Inquiry'),
        ('order', 'Order Issue'),
        ('payment', 'Payment Problem'),
        ('account', 'Account Help'),
        ('product', 'Product Question'),
        ('shipping', 'Shipping & Delivery'),
        ('returns', 'Returns & Refunds'),
        ('technical', 'Technical Issue'),
        ('vendor', 'Vendor Support'),
        ('bug_report', 'Bug Report'),
        ('feedback', 'Feedback'),
        ('other', 'Other'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('pending_customer', 'Pending Customer'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    # Basic information
    ticket_number = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='account_support_tickets')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, **NULL, related_name='assigned_account_tickets')
    
    # Ticket details
    ticket_type = models.CharField(max_length=20, choices=TICKET_TYPES)
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    subject = models.CharField(max_length=200)
    description = models.TextField()
    
    # Related objects
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, **NULL, related_name='account_support_tickets')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, **NULL, related_name='account_support_tickets')
    
    # Attachments
    attachments = models.JSONField(default=list, **NULL)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(**NULL)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Ticket {self.ticket_number} - {self.subject}"
    
    def save(self, *args, **kwargs):
        if not self.ticket_number:
            import uuid
            self.ticket_number = f"TKT-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class Feedback(models.Model):
    """User feedback and suggestions"""
    
    FEEDBACK_TYPES = [
        ('general', 'General Feedback'),
        ('feature_request', 'Feature Request'),
        ('improvement', 'Improvement Suggestion'),
        ('ux', 'User Experience'),
        ('performance', 'Performance Issue'),
        ('design', 'Design Feedback'),
        ('content', 'Content Suggestion'),
        ('vendor', 'Vendor Experience'),
        ('app_store', 'App Store Review'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedback')
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES)
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Ratings
    overall_rating = models.PositiveIntegerField(**NULL)  # 1-5
    ease_of_use_rating = models.PositiveIntegerField(**NULL)
    features_rating = models.PositiveIntegerField(**NULL)
    performance_rating = models.PositiveIntegerField(**NULL)
    
    # Additional information
    is_anonymous = models.BooleanField(default=False)
    device_info = models.JSONField(default=dict, **NULL)
    app_version = models.CharField(max_length=20, **NULL)
    
    # Status
    is_processed = models.BooleanField(default=False)
    admin_notes = models.TextField(**NULL)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Feedback from {self.user.email if not self.is_anonymous else 'Anonymous'} - {self.title}"


class BugReport(models.Model):
    """Bug reports from users"""
    
    BUG_TYPES = [
        ('app_crash', 'App Crash'),
        ('login_issues', 'Login Issues'),
        ('payment_problems', 'Payment Problems'),
        ('search_not_working', 'Search Not Working'),
        ('images_not_loading', 'Images Not Loading'),
        ('slow_performance', 'Slow Performance'),
        ('ui_display_issues', 'UI/Display Issues'),
        ('notification_problems', 'Notification Problems'),
        ('cart_issues', 'Cart Issues'),
        ('profile_settings', 'Profile/Settings'),
        ('messaging_problems', 'Messaging Problems'),
        ('other', 'Other'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    FREQUENCY_CHOICES = [
        ('always', 'Always'),
        ('often', 'Often'),
        ('sometimes', 'Sometimes'),
        ('rarely', 'Rarely'),
        ('once', 'Once'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bug_reports')
    bug_type = models.CharField(max_length=25, choices=BUG_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    steps_to_reproduce = models.TextField(**NULL)
    expected_behavior = models.TextField(**NULL)
    actual_behavior = models.TextField(**NULL)
    
    # Technical information
    device_info = models.JSONField(default=dict, **NULL)
    app_version = models.CharField(max_length=20, **NULL)
    os_version = models.CharField(max_length=20, **NULL)
    browser_info = models.CharField(max_length=100, **NULL)
    
    # Attachments
    screenshots = models.JSONField(default=list, **NULL)
    log_files = models.JSONField(default=list, **NULL)
    
    # Status
    status = models.CharField(max_length=20, choices=[
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ], default='open')
    
    admin_notes = models.TextField(**NULL)
    resolution = models.TextField(**NULL)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Bug Report: {self.title} - {self.get_severity_display()}"
