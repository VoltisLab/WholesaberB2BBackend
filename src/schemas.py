import graphene
import graphql_jwt

from django.core.exceptions import ObjectDoesNotExist
from graphql import GraphQLError
from graphql_auth import mutations
from graphql_auth.bases import DynamicArgsMixin, MutationMixin
from graphql_auth.mixins import ObtainJSONWebTokenMixin, RegisterMixin
from graphql_auth.settings import graphql_auth_settings as app_settings
from graphql_auth.shortcuts import get_user_by_email
from graphql_auth.utils import normalize_fields
from graphql_jwt.exceptions import JSONWebTokenError
from graphql_jwt.utils import get_payload, get_user_by_payload
from accounts.schema.mutations import accounts_mutations
from accounts.schema.account_mutations import AccountMutations
from non_modular_schema.mutations import non_modular_mutations
from products.schema.mutations import product_mutations
from products.schema.queries import product_queries
from accounts.schema.queries import accounts_query
from accounts.schema.account_queries import AccountQueries
from accounts.schema.types.accounts_type import UserType
from security.schema.mutations import security_mutations
from orders.schema.mutations import OrderMutations
from orders.schema.queries import OrderQueries
from reviews.schema.mutations import ReviewMutations
from reviews.schema.queries import ReviewQueries



class NewRegister(
    MutationMixin,
    DynamicArgsMixin,
    RegisterMixin,
    graphene.Mutation,
):
    __doc__ = RegisterMixin.__doc__

    password_fields = (
        []
        if app_settings.ALLOW_PASSWORDLESS_REGISTRATION
        else ["password1", "password2"]
    )
    _required_args = normalize_fields(
        app_settings.REGISTER_MUTATION_FIELDS, password_fields
    )
    _args = app_settings.REGISTER_MUTATION_FIELDS_OPTIONAL

    @staticmethod
    def mutate(root, info, **kwargs):
        
        result = super(NewRegister, NewRegister).mutate(root, info, **kwargs)


        if result.success:
            token = result.token
            payload = get_payload(token)
            user = get_user_by_payload(payload)

        return result



class NewObtainJSONWebToken(
    MutationMixin, ObtainJSONWebTokenMixin, graphql_jwt.JSONWebTokenMutation
):
    __doc__ = ObtainJSONWebTokenMixin.__doc__
    user = graphene.Field(UserType)
    unarchiving = graphene.Boolean(default_value=False)
    use_2fa = graphene.Boolean()
    use_google_authenticator = graphene.Boolean()

    @classmethod
    def Field(cls, *args, **kwargs):
        cls._meta.arguments.update({"password": graphene.String(required=True)})
        for field in app_settings.LOGIN_ALLOWED_FIELDS:
            cls._meta.arguments.update({field: graphene.String()})
        return super(graphql_jwt.JSONWebTokenMutation, cls).Field(*args, **kwargs)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        try:
            # Call the parent mutate method to handle authentication
            username = kwargs.get("username")
            if username:
                kwargs["username"] = username.lower()

            result = super().mutate(root, info, **kwargs)
            if not result.success:
                raise JSONWebTokenError("Please enter valid credentials")
            return result
        except JSONWebTokenError as e:
            # Raise a GraphQL error with a meaningful message
            raise GraphQLError(str(e))


class CustomResendActivationEmail(
    mutations.ResendActivationEmail,
):
    @classmethod
    def mutate(cls, root, info, **kwargs):
        email = kwargs.get("email")
        try:
            user = get_user_by_email(email)
            if user.is_active and user.status.verified:
                raise GraphQLError("User already verified")

            return cls(success=True)
        except ObjectDoesNotExist:
            raise GraphQLError("User with this email does not exist")
        except Exception as e:
            raise GraphQLError(str(e))


class AuthMutation(graphene.ObjectType):
    register = NewRegister.Field()
    login = NewObtainJSONWebToken.Field()  # Login
    resend_activation_email = CustomResendActivationEmail.Field()
    # password_change = mutations.PasswordChange.Field()
    # logout = accounts_mutations.LogoutMutation.Field()
    archive_account = mutations.ArchiveAccount.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


class Mutation(
    AuthMutation,
    accounts_mutations.Mutation,
    AccountMutations,
    product_mutations.Mutation,
    security_mutations.Mutation,
    non_modular_mutations.Mutation,
    OrderMutations,
    ReviewMutations,
):
    pass


class Query(
    accounts_query.Query,
    AccountQueries,
    product_queries.Query,
    OrderQueries,
    ReviewQueries,
    accounts_mutations.Is2FAEnabled,
    accounts_mutations.GetActiveSessions,
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
