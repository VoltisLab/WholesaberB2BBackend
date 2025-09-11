import graphene
from graphene_django import DjangoObjectType
from accounts.schema.types.accounts_type import UserType
from notifications.models import Notification, NotificationPreference


class NotificationType(DjangoObjectType):
    class Meta:
        model = Notification
        fields = "__all__"

    sender = graphene.Field(lambda: SenderType)


class NotificationPreferenceType(DjangoObjectType):
    user = graphene.Field(UserType)
    class Meta:
        model = NotificationPreference
        fields = (
            "user",
            "inapp_notifications",
            "is_push_notification",
            "is_email_notification",
            "email_notifications",
        )


class SenderType(graphene.ObjectType):
    username = graphene.String()
    thumbnail_url = graphene.String()
    profile_picture_url = graphene.String()
