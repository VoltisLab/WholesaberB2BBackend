import graphene
from accounts.choices import (
    GenderChoice,
)


class GenderEnum(graphene.Enum):
    MALE = GenderChoice.MALE.value
    FEMALE = GenderChoice.FEMALE.value
    ANY = GenderChoice.ANY.value

