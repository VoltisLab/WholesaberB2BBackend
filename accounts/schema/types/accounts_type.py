import graphene
from graphene_django import DjangoObjectType

from accounts.models import (
    User,
    DeliveryAddress,
)


class UserType(DjangoObjectType):
    gender = graphene.String()
    class Meta:
        model = User
        exclude = ("is_superuser", "password")
    
    def resolve_gender(self, info):
        return self.gender

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
