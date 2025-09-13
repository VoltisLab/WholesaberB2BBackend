import graphene
from products.schema.enums.product_enums import (
    ClientOrderStatusEnum,
    ConditionEnum,
    DeliveryProviderEnum,
    DeliveryTypeEnum,
    ImageActionEnum,
    ParentCategoryEnum,
    ProductStatusEnum,
    StyleEnum,
)


class ImagesInputType(graphene.InputObjectType):
    url = graphene.String(required=True)
    thumbnail = graphene.String(required=True)


class ImageUpdateInputType(graphene.InputObjectType):
    images = graphene.List(ImagesInputType, required=True)
    action = ImageActionEnum(required=True)


class ProductFiltersInput(graphene.InputObjectType):
    name = graphene.String()
    brand = graphene.Int()
    category = graphene.Int()
    parent_category = ParentCategoryEnum()
    size = graphene.Int()
    custom_brand = graphene.String()
    min_price = graphene.Float()
    max_price = graphene.Float()
    status = graphene.Argument(ProductStatusEnum)
    style = graphene.Argument(StyleEnum)
    condition = graphene.Argument(ConditionEnum)
    discount_price = graphene.Boolean()
    hashtags = graphene.List(graphene.String)
    colors = graphene.List(graphene.String)


class OrderFiltersInput(graphene.InputObjectType):
    status = graphene.Argument(ClientOrderStatusEnum)
    is_seller = graphene.Boolean()


class MultibuyInputType(graphene.InputObjectType):
    id = graphene.Int()
    min_items = graphene.Int(required=True)
    discount_percentage = graphene.Decimal(required=True)
    is_active = graphene.Boolean(default_value=True)


class DeliveryAddressInputType(graphene.InputObjectType):
    address = graphene.String(required=True)
    city = graphene.String(required=True)
    state = graphene.String(required=True)
    country = graphene.String(required=True)
    postal_code = graphene.String(required=True)
    phone_number = graphene.String(required=True)


class DeliveryDetailsInputType(graphene.InputObjectType):
    delivery_address = DeliveryAddressInputType(required=True)
    delivery_provider = DeliveryProviderEnum(required=True)
    delivery_type = DeliveryTypeEnum(required=True)
