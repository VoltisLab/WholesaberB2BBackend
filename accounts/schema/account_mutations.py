import graphene
from graphql import GraphQLError
from django.db import transaction
from django.utils import timezone

from accounts.models import (
    User, DeliveryAddress, NotificationPreference, VendorProfile,
    PaymentMethod, SupportTicket, Feedback, BugReport
)
from accounts.schema.account_types import (
    DeliveryAddressType, PaymentMethodType, NotificationPreferenceType,
    VendorProfileType, SupportTicketType, FeedbackType, BugReportType
)


class CreateAddressMutation(graphene.Mutation):
    """Create a new delivery address"""
    
    class Arguments:
        name = graphene.String(required=True)
        phone_number = graphene.String(required=True)
        street_address = graphene.String(required=True)
        city = graphene.String(required=True)
        state = graphene.String()
        country = graphene.String(default_value="United States")
        postal_code = graphene.String(required=True)
        address_type = graphene.String(default_value="home")
        is_default = graphene.Boolean(default_value=False)
        latitude = graphene.Float()
        longitude = graphene.Float()
        instructions = graphene.String()
    
    address = graphene.Field(DeliveryAddressType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("Authentication required")
        
        try:
            with transaction.atomic():
                # If setting as default, unset other defaults
                if kwargs.get('is_default', False):
                    DeliveryAddress.objects.filter(user=user, is_default=True).update(is_default=False)
                
                address = DeliveryAddress.objects.create(
                    user=user,
                    **kwargs
                )
                
                return CreateAddressMutation(
                    address=address,
                    success=True,
                    message="Address created successfully"
                )
                
        except Exception as e:
            raise GraphQLError(f"Failed to create address: {str(e)}")


class UpdateAddressMutation(graphene.Mutation):
    """Update an existing delivery address"""
    
    class Arguments:
        address_id = graphene.ID(required=True)
        name = graphene.String()
        phone_number = graphene.String()
        street_address = graphene.String()
        city = graphene.String()
        state = graphene.String()
        country = graphene.String()
        postal_code = graphene.String()
        address_type = graphene.String()
        is_default = graphene.Boolean()
        latitude = graphene.Float()
        longitude = graphene.Float()
        instructions = graphene.String()
    
    address = graphene.Field(DeliveryAddressType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, address_id, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("Authentication required")
        
        try:
            address = DeliveryAddress.objects.get(id=address_id, user=user)
            
            with transaction.atomic():
                # If setting as default, unset other defaults
                if kwargs.get('is_default', False):
                    DeliveryAddress.objects.filter(user=user, is_default=True).update(is_default=False)
                
                for field, value in kwargs.items():
                    if value is not None:
                        setattr(address, field, value)
                
                address.save()
                
                return UpdateAddressMutation(
                    address=address,
                    success=True,
                    message="Address updated successfully"
                )
                
        except DeliveryAddress.DoesNotExist:
            raise GraphQLError("Address not found")
        except Exception as e:
            raise GraphQLError(f"Failed to update address: {str(e)}")


class DeleteAddressMutation(graphene.Mutation):
    """Delete a delivery address"""
    
    class Arguments:
        address_id = graphene.ID(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, address_id):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("Authentication required")
        
        try:
            address = DeliveryAddress.objects.get(id=address_id, user=user)
            address.delete()
            
            return DeleteAddressMutation(
                success=True,
                message="Address deleted successfully"
            )
            
        except DeliveryAddress.DoesNotExist:
            raise GraphQLError("Address not found")
        except Exception as e:
            raise GraphQLError(f"Failed to delete address: {str(e)}")


class UpdateNotificationPreferencesMutation(graphene.Mutation):
    """Update user notification preferences"""
    
    class Arguments:
        push_notifications = graphene.Boolean()
        push_orders = graphene.Boolean()
        push_promotions = graphene.Boolean()
        push_messages = graphene.Boolean()
        push_reviews = graphene.Boolean()
        email_notifications = graphene.Boolean()
        email_orders = graphene.Boolean()
        email_promotions = graphene.Boolean()
        email_messages = graphene.Boolean()
        email_reviews = graphene.Boolean()
        email_newsletter = graphene.Boolean()
        sms_notifications = graphene.Boolean()
        sms_orders = graphene.Boolean()
        sms_promotions = graphene.Boolean()
    
    preferences = graphene.Field(NotificationPreferenceType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("Authentication required")
        
        try:
            preferences, created = NotificationPreference.objects.get_or_create(user=user)
            
            for field, value in kwargs.items():
                if value is not None:
                    setattr(preferences, field, value)
            
            preferences.save()
            
            return UpdateNotificationPreferencesMutation(
                preferences=preferences,
                success=True,
                message="Notification preferences updated successfully"
            )
            
        except Exception as e:
            raise GraphQLError(f"Failed to update preferences: {str(e)}")


class CreateSupportTicketMutation(graphene.Mutation):
    """Create a support ticket"""
    
    class Arguments:
        ticket_type = graphene.String(required=True)
        priority = graphene.String(default_value="medium")
        subject = graphene.String(required=True)
        description = graphene.String(required=True)
        order_id = graphene.ID()
        product_id = graphene.ID()
        attachments = graphene.List(graphene.String)
    
    ticket = graphene.Field(SupportTicketType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("Authentication required")
        
        try:
            ticket = SupportTicket.objects.create(
                user=user,
                **kwargs
            )
            
            return CreateSupportTicketMutation(
                ticket=ticket,
                success=True,
                message="Support ticket created successfully"
            )
            
        except Exception as e:
            raise GraphQLError(f"Failed to create support ticket: {str(e)}")


class CreateFeedbackMutation(graphene.Mutation):
    """Create user feedback"""
    
    class Arguments:
        feedback_type = graphene.String(required=True)
        title = graphene.String(required=True)
        message = graphene.String(required=True)
        overall_rating = graphene.Int()
        ease_of_use_rating = graphene.Int()
        features_rating = graphene.Int()
        performance_rating = graphene.Int()
        is_anonymous = graphene.Boolean(default_value=False)
        device_info = graphene.JSONString()
        app_version = graphene.String()
    
    feedback = graphene.Field(FeedbackType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("Authentication required")
        
        try:
            feedback = Feedback.objects.create(
                user=user,
                **kwargs
            )
            
            return CreateFeedbackMutation(
                feedback=feedback,
                success=True,
                message="Feedback submitted successfully"
            )
            
        except Exception as e:
            raise GraphQLError(f"Failed to submit feedback: {str(e)}")


class CreateBugReportMutation(graphene.Mutation):
    """Create a bug report"""
    
    class Arguments:
        bug_type = graphene.String(required=True)
        severity = graphene.String(required=True)
        frequency = graphene.String(required=True)
        title = graphene.String(required=True)
        description = graphene.String(required=True)
        steps_to_reproduce = graphene.String()
        expected_behavior = graphene.String()
        actual_behavior = graphene.String()
        device_info = graphene.JSONString()
        app_version = graphene.String()
        os_version = graphene.String()
        browser_info = graphene.String()
        screenshots = graphene.List(graphene.String)
        log_files = graphene.List(graphene.String)
    
    bug_report = graphene.Field(BugReportType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("Authentication required")
        
        try:
            bug_report = BugReport.objects.create(
                user=user,
                **kwargs
            )
            
            return CreateBugReportMutation(
                bug_report=bug_report,
                success=True,
                message="Bug report submitted successfully"
            )
            
        except Exception as e:
            raise GraphQLError(f"Failed to submit bug report: {str(e)}")


class AccountMutations(graphene.ObjectType):
    create_address = CreateAddressMutation.Field()
    update_address = UpdateAddressMutation.Field()
    delete_address = DeleteAddressMutation.Field()
    update_notification_preferences = UpdateNotificationPreferencesMutation.Field()
    create_support_ticket = CreateSupportTicketMutation.Field()
    create_feedback = CreateFeedbackMutation.Field()
    create_bug_report = CreateBugReportMutation.Field()
