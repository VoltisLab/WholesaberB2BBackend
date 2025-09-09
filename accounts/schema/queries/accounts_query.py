import graphene
from django.utils import timezone

from graphql_jwt.decorators import login_required

from accounts.schema.types.accounts_type import UserType
from accounts.models import User


class Query(graphene.ObjectType):
    pagination_result = None
    view_me = graphene.Field(UserType)
    
    @login_required
    def resolve_view_me(self, info, **kwargs):
        return info.context.user

