import graphene
from graphene_django import DjangoObjectType
from django.db.models import Q

from accounts.models import (
    DeliveryAddress, NotificationPreference, VendorProfile,
    PaymentMethod, SupportTicket, Feedback, BugReport
)
from accounts.schema.account_types import (
    DeliveryAddressType, PaymentMethodType, NotificationPreferenceType,
    VendorProfileType, SupportTicketType, FeedbackType, BugReportType
)


class AccountQueries(graphene.ObjectType):
    """Account-related queries"""
    
    # Address queries
    my_addresses = graphene.List(DeliveryAddressType)
    address_by_id = graphene.Field(DeliveryAddressType, address_id=graphene.ID(required=True))
    default_address = graphene.Field(DeliveryAddressType)
    
    # Payment method queries
    my_payment_methods = graphene.List(PaymentMethodType)
    payment_method_by_id = graphene.Field(PaymentMethodType, payment_method_id=graphene.ID(required=True))
    
    # Notification preferences
    my_notification_preferences = graphene.Field(NotificationPreferenceType)
    
    # Vendor profile
    my_vendor_profile = graphene.Field(VendorProfileType)
    vendor_profile_by_id = graphene.Field(VendorProfileType, vendor_id=graphene.ID(required=True))
    
    # Support queries
    my_support_tickets = graphene.List(SupportTicketType, status=graphene.String())
    support_ticket_by_id = graphene.Field(SupportTicketType, ticket_id=graphene.ID(required=True))
    
    # Feedback queries
    my_feedback = graphene.List(FeedbackType)
    feedback_by_id = graphene.Field(FeedbackType, feedback_id=graphene.ID(required=True))
    
    # Bug report queries
    my_bug_reports = graphene.List(BugReportType, status=graphene.String())
    bug_report_by_id = graphene.Field(BugReportType, bug_report_id=graphene.ID(required=True))
    
    def resolve_my_addresses(self, info):
        """Get all addresses for the authenticated user"""
        user = info.context.user
        if not user.is_authenticated:
            return []
        
        return DeliveryAddress.objects.filter(user=user).order_by('-is_default', '-created_at')
    
    def resolve_address_by_id(self, info, address_id):
        """Get a specific address by ID"""
        user = info.context.user
        if not user.is_authenticated:
            return None
        
        try:
            return DeliveryAddress.objects.get(id=address_id, user=user)
        except DeliveryAddress.DoesNotExist:
            return None
    
    def resolve_default_address(self, info):
        """Get the user's default address"""
        user = info.context.user
        if not user.is_authenticated:
            return None
        
        try:
            return DeliveryAddress.objects.get(user=user, is_default=True)
        except DeliveryAddress.DoesNotExist:
            return None
    
    def resolve_my_payment_methods(self, info):
        """Get all payment methods for the authenticated user"""
        user = info.context.user
        if not user.is_authenticated:
            return []
        
        return PaymentMethod.objects.filter(user=user, is_active=True).order_by('-is_default', '-created_at')
    
    def resolve_payment_method_by_id(self, info, payment_method_id):
        """Get a specific payment method by ID"""
        user = info.context.user
        if not user.is_authenticated:
            return None
        
        try:
            return PaymentMethod.objects.get(id=payment_method_id, user=user)
        except PaymentMethod.DoesNotExist:
            return None
    
    def resolve_my_notification_preferences(self, info):
        """Get notification preferences for the authenticated user"""
        user = info.context.user
        if not user.is_authenticated:
            return None
        
        preferences, created = NotificationPreference.objects.get_or_create(user=user)
        return preferences
    
    def resolve_my_vendor_profile(self, info):
        """Get vendor profile for the authenticated user"""
        user = info.context.user
        if not user.is_authenticated:
            return None
        
        try:
            return VendorProfile.objects.get(user=user)
        except VendorProfile.DoesNotExist:
            return None
    
    def resolve_vendor_profile_by_id(self, info, vendor_id):
        """Get vendor profile by vendor ID"""
        try:
            from accounts.models import User
            vendor = User.objects.get(id=vendor_id)
            return VendorProfile.objects.get(user=vendor)
        except (User.DoesNotExist, VendorProfile.DoesNotExist):
            return None
    
    def resolve_my_support_tickets(self, info, status=None):
        """Get support tickets for the authenticated user"""
        user = info.context.user
        if not user.is_authenticated:
            return []
        
        queryset = SupportTicket.objects.filter(user=user)
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-created_at')
    
    def resolve_support_ticket_by_id(self, info, ticket_id):
        """Get a specific support ticket by ID"""
        user = info.context.user
        if not user.is_authenticated:
            return None
        
        try:
            return SupportTicket.objects.get(id=ticket_id, user=user)
        except SupportTicket.DoesNotExist:
            return None
    
    def resolve_my_feedback(self, info):
        """Get feedback submitted by the authenticated user"""
        user = info.context.user
        if not user.is_authenticated:
            return []
        
        return Feedback.objects.filter(user=user).order_by('-created_at')
    
    def resolve_feedback_by_id(self, info, feedback_id):
        """Get a specific feedback by ID"""
        user = info.context.user
        if not user.is_authenticated:
            return None
        
        try:
            return Feedback.objects.get(id=feedback_id, user=user)
        except Feedback.DoesNotExist:
            return None
    
    def resolve_my_bug_reports(self, info, status=None):
        """Get bug reports submitted by the authenticated user"""
        user = info.context.user
        if not user.is_authenticated:
            return []
        
        queryset = BugReport.objects.filter(user=user)
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-created_at')
    
    def resolve_bug_report_by_id(self, info, bug_report_id):
        """Get a specific bug report by ID"""
        user = info.context.user
        if not user.is_authenticated:
            return None
        
        try:
            return BugReport.objects.get(id=bug_report_id, user=user)
        except BugReport.DoesNotExist:
            return None
