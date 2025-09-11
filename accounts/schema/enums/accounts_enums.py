import graphene
from accounts.choices import (
    GenderChoice,
    AccountType,
)


class GenderEnum(graphene.Enum):
    MALE = GenderChoice.MALE.value
    FEMALE = GenderChoice.FEMALE.value
    OTHER = GenderChoice.OTHER.value
    PREFER_NOT_TO_SAY = GenderChoice.PREFER_NOT_TO_SAY.value


class SearchTypeEnum(graphene.Enum):
    USER = "USER"
    PRODUCT = "PRODUCT"


class AccountTypeEnum(graphene.Enum):
    CUSTOMER = AccountType.CUSTOMER.value
    SUPPLIER = AccountType.SUPPLIER.value


class AddressTypeEnum(graphene.Enum):
    HOME = "HOME"
    WORK = "WORK"
    OTHER = "OTHER"
