from django.db import models
from accounts.models import User
from notifications.choices import NotificationChoices

NOTIFICATION_TYPE_CHOICES = NotificationChoices.choices


class Notification(models.Model):
    room = models.ForeignKey("NotificationRoom", on_delete=models.CASCADE, null=True)
    sender = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="sent_notifications"
    )
    message = models.CharField(max_length=500)
    model = models.CharField(max_length=100)
    model_id = models.CharField(max_length=200)
    model_group = models.CharField(max_length=100, null=True)
    is_read = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    meta = models.JSONField(default=list, null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)


class NotificationRoom(models.Model):
    member = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class NotificationPreference(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="notification_preferences"
    )
    is_push_notification = models.BooleanField(default=True)
    is_email_notification = models.BooleanField(default=True)
    inapp_notifications = models.JSONField(default=dict)
    email_notifications = models.JSONField(default=dict)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize default preferences if not set
        if not self.inapp_notifications:
            self.inapp_notifications = {
                notification: True for notification, _ in NOTIFICATION_TYPE_CHOICES
            }
        if not self.email_notifications:
            self.email_notifications = {
                notification: False for notification, _ in NOTIFICATION_TYPE_CHOICES
            }