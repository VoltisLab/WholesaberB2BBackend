import graphene
from graphene_django import DjangoObjectType
from accounts.models import (
    DeliveryAddress, NotificationPreference, VendorProfile,
    PaymentMethod, SupportTicket, Feedback, BugReport
)


class DeliveryAddressType(DjangoObjectType):
    class Meta:
        model = DeliveryAddress
        fields = "__all__"


class PaymentMethodType(DjangoObjectType):
    class Meta:
        model = PaymentMethod
        fields = "__all__"


class NotificationPreferenceType(DjangoObjectType):
    class Meta:
        model = NotificationPreference
        fields = "__all__"


class VendorProfileType(DjangoObjectType):
    class Meta:
        model = VendorProfile
        fields = "__all__"


class SupportTicketType(DjangoObjectType):
    class Meta:
        model = SupportTicket
        fields = "__all__"


class FeedbackType(DjangoObjectType):
    class Meta:
        model = Feedback
        fields = "__all__"


class BugReportType(DjangoObjectType):
    class Meta:
        model = BugReport
        fields = "__all__"
