import graphene
from graphene_django import DjangoObjectType

from accounts.models import (
    User,
    DeliveryAddress,
)


class UserType(DjangoObjectType):
    class Meta:
        model = User
        exclude = ("is_superuser", "password")


class DeliveryAddressType(DjangoObjectType):
    user = graphene.Field(UserType)

    class Meta:
        model = DeliveryAddress
        fields = (
            "id",
            "user",
            "address_type",
            "country",
            "state",
            "city",
            "street_address",
            "postal_code",
            "created_at",
            "is_default",
            "updated_at",
        )
