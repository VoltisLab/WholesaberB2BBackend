from django.db import models
from accounts.models import User

NULL = {"null": True, "blank": True}


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
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_tickets')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, **NULL, related_name='assigned_tickets')
    
    # Ticket details
    ticket_type = models.CharField(max_length=20, choices=TICKET_TYPES)
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    subject = models.CharField(max_length=200)
    description = models.TextField()
    
    # Related objects
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, **NULL)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, **NULL)
    
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
    bug_type = models.CharField(max_length=20, choices=BUG_TYPES)
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
