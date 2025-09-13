# import channels_graphql_ws
# import graphene

# from notifications.schema.types.notification_types import NotificationType



# class NewNotification(channels_graphql_ws.Subscription):
#     notification = graphene.Field(NotificationType)

#     class Arguments:
#         notification_room = graphene.String()

#     def subscribe(cls, info, notification_room=None):
#         return [notification_room] if notification_room is not None else None
    
#     def publish(notification, info, notification_room):
#         return NewNotification(
#             notification=notification
#         )

# class Subscription(graphene.ObjectType):
#     new_notification= NewNotification.Field()