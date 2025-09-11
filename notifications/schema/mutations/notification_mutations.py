import graphene
import jinja2
from django.conf import settings
from django.template.loader import render_to_string
from accounts.models import User
from notifications.models import Notification, NotificationPreference, NotificationRoom
from notifications.schema.inputs.notification_inputs import (
    NotificationsPreferenceInputType,
)
from notifications.schema.notification_responses import (
    NOTIFICATION_NOT_FOUND,
)
from celery import shared_task
from django.core.mail import send_mail
from graphql_jwt.decorators import login_required
from notifications.schema.types.notification_types import NotificationPreferenceType
from utils.non_modular_utils.errors import ErrorException, StandardError
from utils.utils import get_template_path
from utils.jobs.base import only_one, BaseTaskWithRetry

class CreateNotification(object):

    @shared_task(bind=True, base=BaseTaskWithRetry, name="create_notification")
    @only_one
    @staticmethod
    def create_notification(
        self,
        user_id: int,
        sender: int,
        message: str,
        model: str,
        model_id: int,
        model_group: str,
        title: str,
        info: dict,
        meta: dict = {},
    ) -> None:
        user = User.objects.get(id=user_id)

        # The email recipient value is used to dynamically determine the email recipient.
        email_recipient_value = meta.pop("email_recipient", None)
        email_recipient = email_recipient_value if email_recipient_value else user.email

        room, _ = NotificationRoom.objects.get_or_create(member=user)
        sender = User.objects.get(id=sender)
        Notification.objects.create(
            message=f"{title} {message}",
            sender=sender,
            model=model,
            model_id=model_id,
            model_group=model_group,
            room=room,
            meta=meta,
        )

        data = {
            "title": title.capitalize() or "New notification",
            "message": message,
            "page": info["page"],
            "object_id": str(info["object_id"]),
            "conversation_id": info.get("conversation_id", None),
        }
        for key in ["is_offer", "is_order", "chat"]:
            if key in info:
                data[key] = info[key]

        if "media_thumbnail" in meta:
            data["media_thumbnail"] = str(meta["media_thumbnail"])

        # Send firebase notification
        # if NotificationUtils.should_send_push_notification(user, message):
        #     send_firebase_notification(user.fcm_tokens, data)

        html_body = None
        subject = None
        # device_info = meta.get("device_info", {})

        if "has been confirmed." in message:
            template_path = get_template_path("order_confirmation")
            html = open(
                template_path,
                "r",
            )
            subject = f"Order Confirmation - #{meta['email_context']['order_id']}"
            body = html.read()
            html_body = jinja2.Template(body)

        # elif message in ["Followed you.", "Wants to connect."]:
        #     template_path = get_template_path("followed_you", "notifications")
        #     html = open(
        #         template_path,
        #         "r",
        #     )
        #     subject = f"{title} followed you"
        #     body = html.read()
        #     html_body = jinja2.Template(body)
        elif message in ["deleted your account"]:
            template_path = get_template_path("account_deletion_notice")
            html = open(
                template_path,
                "r",
            )
            subject = f"Account Deletion Notice"
            body = html.read()
            html_body = jinja2.Template(body)
        else:
            pass

        # Send email notification
        # send_email_notification = NotificationUtils.should_send_email_notification(
        #     user, message
        # )
        # print("email_context: ", meta.get("email_context", {}))
        # if html_body and subject and send_email_notification:
        #     html_message = html_body.render(
        #         {
        #             "username": user.username,
        #             "title": title,
        #             "message": message.lower(),
        #             "context": meta.get("email_context", {}),
        #         }
        #     )
        #     send_mail(
        #         subject,
        #         message="body",
        #         from_email=settings.DEFAULT_FROM_EMAIL,
        #         recipient_list=[email_recipient],
        #         html_message=html_message,
        #     )
    
    
    @shared_task(bind=True, base=BaseTaskWithRetry, name="send_contact_message")
    @only_one
    @staticmethod
    def send_contact_message(self, **kwargs:dict):
        """Sends a contact form message to Voltis Labs' email."""
        subject = "New Contact Form Submission"
        recipient_email = kwargs.get("recipient_email")

        context = {
            'sender_email': kwargs.get("sender_email"),
            'name': kwargs.get("name", "Anonymous"),
            'message': kwargs.get("message"),
        }
        html_message = render_to_string('email/contact_form_message.html', context)
        send_mail(
            subject=subject,
            message="body",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            html_message=html_message,
        )

class ReadNotifications(graphene.Mutation):
    class Arguments:
        notification_ids = graphene.List(graphene.Int)

    success = graphene.Boolean()

    @login_required
    def mutate(self, info, **kwargs):
        notification_ids = kwargs.get("notification_ids")
        notifications = Notification.objects.filter(
            id__in=notification_ids, deleted=False
        )
        notifications.update(is_read=True)

        return ReadNotifications(success=True)


class DeleteNotification(graphene.Mutation):
    class Arguments:
        notification_id = graphene.Int(required=True)

    success = graphene.Boolean()

    @login_required
    def mutate(self, info, notification_id: int) -> "DeleteNotification":
        try:
            notification = Notification.objects.get(id=notification_id)
            notification.deleted = True
            notification.save()

            return DeleteNotification(success=True)
        except Notification.DoesNotExist:
            raise ErrorException(
                message=NOTIFICATION_NOT_FOUND.format(notification_id),
                error_type=StandardError,
                meta={},
                code=404,
            )


class UpdateNotificationPreference(graphene.Mutation):
    """
    Mutation to update user notification preferences.

    Allows updating push and email notification settings, as well as
    in-app and email notification details. Can also turn off all notifications
    with a single flag.

    If is_all_notifications_off is True, it overrides other inputs and
    disables all notifications. Otherwise, it updates individual settings
    based on the provided inputs.
    """

    class Arguments:
        is_push_notification = graphene.Boolean(required=True)
        is_email_notification = graphene.Boolean(required=True)
        is_silent_mode_on = graphene.Boolean(required=True)
        inapp_notifications = NotificationsPreferenceInputType()
        email_notifications = NotificationsPreferenceInputType()

    success = graphene.Boolean()
    notification_preference = graphene.Field(NotificationPreferenceType)

    @login_required
    def mutate(self, info, **kwargs):
        is_push_notification = kwargs.get("is_push_notification")
        is_email_notification = kwargs.get("is_email_notification")
        inapp_notifications = kwargs.get("inapp_notifications")
        email_notifications = kwargs.get("email_notifications")
        is_silent_mode_on = kwargs.get("is_silent_mode_on", False)
        user = info.context.user

        try:
            notification_preference = user.notification_preferences
        except NotificationPreference.DoesNotExist:
            raise Exception("Notification preferences not found.")

        if is_silent_mode_on:
            # Turn off all notifications
            notification_preference.is_push_notification = False
            notification_preference.is_email_notification = False
        else:
            # Update individual notification settings
            if is_push_notification is not None:
                notification_preference.is_push_notification = is_push_notification
                if is_push_notification and inapp_notifications is not None:
                    notification_preference.inapp_notifications.update(
                        inapp_notifications
                    )

            if is_email_notification is not None:
                notification_preference.is_email_notification = is_email_notification
                if is_email_notification and email_notifications is not None:
                    notification_preference.email_notifications.update(
                        email_notifications
                    )

        notification_preference.save()

        return UpdateNotificationPreference(
            success=True, notification_preference=notification_preference
        )


class Mutation(graphene.ObjectType):
    read_notifications = ReadNotifications.Field(description="Read notification")
    delete_notification = DeleteNotification.Field(description="Delete notification")
    update_notification_preference = UpdateNotificationPreference.Field(
        description="update user notification preferences"
    )
