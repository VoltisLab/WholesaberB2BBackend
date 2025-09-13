import graphene
from django.conf import settings


class FileTypeEnum(graphene.Enum):
    PROFILE_PICTURE = settings.PROFILE_PICTURE
    VIDEO = settings.VIDEO
    RESOURCE = settings.RESOURCES
    PRODUCT = settings.PRODUCT
    BANNER = settings.BANNER
