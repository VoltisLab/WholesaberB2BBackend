import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from notifications.models import Notification
from notifications.serializers import NotificationSerializer


class NotificationConsumer(JsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"notification_{self.room_name}"
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            return
        # private notification group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name,
        )
        self.accept()
        self.send_pending_notifications()

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name,
        )
        return super().disconnect(code)

    def send_notification(self, event):
        text_data_json = event.copy()
        text_data_json.pop("type")
        # Send Notification
        self.send(
            text_data=json.dumps(
                text_data_json
            )
        )
        self.mark_notification_as_delivered(event["id"])
    
    def send_pending_notifications(self):
        pending_notifications = self.get_pending_notifications()
        for notification in pending_notifications:
            chat_type = {"type": "send_notification"}
            serializer = NotificationSerializer(instance=notification)
            return_dict = {
                **chat_type,
                **serializer.data
            }

            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                return_dict
            )

    def get_pending_notifications(self):
        pending_notifications = Notification.objects.filter(room__member=self.user, delivered=False)
        
        return pending_notifications

    def mark_notification_as_delivered(self, notification_id):
        instance = Notification.objects.get(id=int(notification_id))
        instance.delivered = True
        instance.save()
