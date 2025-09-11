import graphene
from notifications.models import Notification, NotificationPreference
from notifications.schema.types.notification_types import (
    NotificationPreferenceType,
    NotificationType,
)

from graphql_jwt.decorators import login_required

from utils.non_modular_utils.database_utils import DatabaseUtil


class Query(graphene.ObjectType):
    pagination_result = None

    notifications = graphene.List(
        NotificationType,
        page_count=graphene.Int(),
        page_number=graphene.Int(),
    )

    notification_preference = graphene.Field(NotificationPreferenceType)
    notifications_total_number = graphene.Int()

    def resolve_notifications(self, info, **kwargs):
        page_count = kwargs.get("page_count", None)
        page_number = kwargs.get("page_number", None)

        notifications = Notification.objects.filter(
            room__member=info.context.user, deleted=False
        )

        # if profile_view:
        #     notifications = notifications.filter(
        #         message__icontains="Viewed your profile."
        #     )

        # Paginate result
        result, total_pages, total_items = DatabaseUtil.paginate_query(
            notifications, page_count, page_number
        )
        Query.pagination_result = (result, total_pages, total_items)
        return result

    @login_required
    def resolve_notifications_total_number(self, info, **kwargs):
        if not Query.pagination_result:
            return 0
        return Query.pagination_result[2]

    @login_required
    def resolve_notification_preference(self, info):
        user = info.context.user
        return NotificationPreference.objects.get(user=user)
