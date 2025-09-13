import graphene
from django.utils import timezone

from graphql_jwt.decorators import login_required

from accounts.schema.types.accounts_type import UserType, DeliveryAddressType
from accounts.models import User, DeliveryAddress


class Query(graphene.ObjectType):
    pagination_result = None
    view_me = graphene.Field(UserType)
    user_delivery_addresses = graphene.List(DeliveryAddressType)

    @login_required
    def resolve_view_me(self, info, **kwargs):
        return info.context.user

    @login_required
    def resolve_user_delivery_addresses(self, info, **kwargs):
        return DeliveryAddress.objects.filter(user=info.context.user).order_by(
            "-is_default"
        )
