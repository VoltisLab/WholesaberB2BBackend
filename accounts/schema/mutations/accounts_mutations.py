import graphene
from datetime import datetime
from django.db.models import Q
from django.core.cache import cache
from graphql_jwt.decorators import login_required
from graphql_jwt.refresh_token.models import RefreshToken
from graphql_jwt.utils import jwt_decode

from accounts.schema.types.accounts_type import UserType
from accounts.schema.inputs.accounts_inputs import (
    ProfilePictureInputType,
)



class LogoutMutation(graphene.Mutation):
    class Arguments:
        refresh_token = graphene.String(required=True)
        fcm_token = graphene.String()

    message = graphene.String()

    @login_required
    def mutate(self, info, **kwargs):
        refresh_token = kwargs.get("refresh_token")
        fcm_token = kwargs.get("fcm_token")
        User = info.context.user
        request = info.context

        try:
            # Extract the access token from the Authorization header
            auth_header = request.META.get("HTTP_AUTHORIZATION", "")
            if auth_header:
                token_type, token = auth_header.split()
                if token_type == "Bearer":
                    # Decode acces token and get it's expiration time
                    payload = jwt_decode(token)
                    exp = payload.get("exp", 0)
                    current_time = datetime.utcnow().timestamp()
                    ttl = exp - current_time

                    # Blacklist access token
                    cache.set(f"blacklisted_token:{token}", True, timeout=ttl)

            if refresh_token:
                refresh_token_obj = RefreshToken.objects.filter(
                    token=refresh_token, user=User
                ).first()
                if refresh_token_obj:
                    refresh_token_obj.delete()
                else:
                    return LogoutMutation(message="Invalid refresh token")

            return LogoutMutation(message="Logout successful")

        except Exception as e:
            return LogoutMutation(message=f"Logout failed: {str(e)}")




class Mutation(graphene.ObjectType):
    logout = LogoutMutation.Field()