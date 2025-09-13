import graphene
from graphql_jwt.decorators import login_required

from products.schema.enums.product_enums import (
    ConditionEnum,
    ParcelSizeEnum,
    StyleEnum,
)
from products.schema.inputs.product_inputs import (
    ImageUpdateInputType,
    ImagesInputType,
)
from products.schema.product_responses import (
    CREATE_PRODUCT_SUCCESS,
    DELETE_PRODUCT_SUCCESS,
    UPDATE_PRODUCT_SUCCESS,
    PRODUCT_REPORTED,
)
from products.schema.types.product_types import (
    ProductType,
)
from utils.non_modular_utils.errors import ErrorException
from utils.product_utils.product_utils import ProductUtils
from utils.non_modular_utils.errors import ErrorException, GenericError, StandardError


class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String(required=True)
        price = graphene.Float(required=True)
        category = graphene.Int(required=True)
        size = graphene.Int()
        images_url = graphene.List(ImagesInputType, required=True)
        discount = graphene.Float()
        condition = ConditionEnum()
        style = StyleEnum()
        color = graphene.List(graphene.String)
        brand = graphene.Int()
        materials = graphene.List(graphene.Int)
        custom_brand = graphene.String()
        is_featured = graphene.Boolean()

    success = graphene.Boolean()
    message = graphene.String()
    product = graphene.Field(ProductType)

    @login_required
    def mutate(self, info, **kwargs):
        product = ProductUtils.create_product(info.context.user, **kwargs)

        return CreateProduct(
            success=True, message=CREATE_PRODUCT_SUCCESS, product=product
        )


class UpdateProduct(graphene.Mutation):
    class Arguments:
        product_id = graphene.Int(required=True)
        name = graphene.String()
        description = graphene.String()
        price = graphene.Float()
        images_url = ImageUpdateInputType()
        discount_price = graphene.Float()
        condition = ConditionEnum()
        parcel_size = ParcelSizeEnum()
        style = StyleEnum()
        category = graphene.Int()
        size = graphene.Int()
        color = graphene.List(graphene.String)
        brand = graphene.Int()
        materials = graphene.List(graphene.Int)
        custom_brand = graphene.String()
        is_featured = graphene.Boolean()

    success = graphene.Boolean()
    message = graphene.String()
    product = graphene.Field(ProductType)

    @login_required
    def mutate(self, info, **kwargs):
        product = ProductUtils.update_product(info.context.user, **kwargs)

        return UpdateProduct(
            success=True, message=UPDATE_PRODUCT_SUCCESS, product=product
        )


class DeleteProduct(graphene.Mutation):
    class Arguments:
        product_id = graphene.Int(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    @login_required
    def mutate(self, info, **kwargs):
        product_id = kwargs.pop("product_id")

        ProductUtils.delete_product(info.context.user, product_id)

        return DeleteProduct(success=True, message=DELETE_PRODUCT_SUCCESS)


class LikeProduct(graphene.Mutation):
    class Arguments:
        product_id = graphene.Int(required=True)

    success = graphene.Boolean()

    @login_required
    def mutate(self, info, **kwargs):
        product_id = kwargs.get("product_id")

        success = ProductUtils.like_product(info.context.user, product_id)

        return LikeProduct(
            success=success,
        )


class ReportProduct(graphene.Mutation):
    class Arguments:
        product_id = graphene.ID(required=True)
        reason = graphene.String(required=True)
        content = graphene.String()

    message = graphene.String()

    @login_required
    def mutate(self, info, **kwargs):
        ProductUtils.report_product(info.context.user, **kwargs)
        return ReportProduct(message=PRODUCT_REPORTED)


class Mutation(graphene.ObjectType):
    create_product = CreateProduct.Field()
    update_product = UpdateProduct.Field()
    delete_product = DeleteProduct.Field()
    like_product = LikeProduct.Field()
    # create_order = CreateOrder.Field()
    # update_order_status = UpdateOrderStatus.Field()
    # cancel_order = CancelOrder.Field()
    # response_to_cancelled_order = RespondToCancelledOrder.Field()
    # create_offer = CreateOffer.Field()
    # create_multibuy_discount = CreateOrUpdateMultibuyDiscount.Field()
    # deactivate_multibuy_discounts = DeactivateMultibuyDiscounts.Field()
    # respond_to_offer = RespondToOffer.Field(description=OFFER_OVERVIEW)
    # report_product = ReportProduct.Field()


# Import shop mutations
from .shop_mutations import ShopMutations
