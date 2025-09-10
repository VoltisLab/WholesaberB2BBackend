import logging

import jwt
from django.core.cache import cache
from graphql import GraphQLError
from graphql_jwt.middleware import allow_any

logger = logging.getLogger(__name__)


class JWTBlacklistMiddleware:
    def resolve(self, next, root, info, **args):
        operation = info.operation.operation if info.operation else None
        field_name = info.field_name
        path = info.path

        # Skip blacklist check for:
        # 1. The "logout" mutation field
        # 2. Any field nested under the "logout" mutation (e.g., "message")
        # 3. Any field or operation in JWT_ALLOW_ANY_CLASSES
        if (
            (operation.value == "mutation" and field_name == "logout")
            or (path and path.prev and path.prev.key == "logout")
            or allow_any(info, **args)  # Fields in JWT_ALLOW_ANY_CLASSES
            # or (path and path.prev and allow_any(info, **args))  # Nested fields under allow-any mutations
        ):
            return next(root, info, **args)

        request = info.context
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")

        if auth_header:
            try:
                token_type, token = auth_header.split()
                if token_type == "Bearer":
                    if cache.get(f"blacklisted_token:{token}"):
                        raise GraphQLError("Token has been revoked")

            except jwt.ExpiredSignatureError:
                raise GraphQLError("Token has expired")
            except jwt.InvalidTokenError:
                raise GraphQLError("Invalid token")

        return next(root, info, **args)


class LastSeenMiddleware:
    def resolve(self, next, root, info, **kwargs):
        request = info.context
        if request.user.is_authenticated:
            from django.utils import timezone

            current_time = timezone.now()
            if (
                not request.user.last_seen
                or (current_time - request.user.last_seen).total_seconds() > 240
            ):
                request.user.last_seen = current_time
                request.user.save(update_fields=["last_seen"])

        return next(root, info, **kwargs)
