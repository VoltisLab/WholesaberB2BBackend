from decimal import Decimal
import graphene
from accounts.schema.types.accounts_type import UserType
from products.choices import OrderStatusChoices
from products.models import (
    Category,
    Product,
    ProductLike,
)
from products.schema.enums.product_enums import SellerResponseEnum
from graphene_django import DjangoObjectType
from django.db.models import (
    Count,
    Sum,
    Q,
    DecimalField,
    Value,
    ExpressionWrapper,
    F,
    Case,
    When,
    IntegerField,
)
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import Coalesce, Cast
from accounts.models import User
from utils.utils import format_price


class ProductType(DjangoObjectType):
    seller = graphene.Field(UserType)
    brand = graphene.Field(lambda: BrandType)
    category = graphene.Field(lambda: CategoryType)
    size = graphene.Field(lambda: SizeType)
    user_liked = graphene.Boolean()
    materials = graphene.List(lambda: BrandType)
    price = graphene.Float()

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "description",
        )

    def resolve_seller(self, info):
        return self.seller

    def resolve_category(self, info):
        return self.category

    def resolve_size(self, info):
        return self.size

    def resolve_user_liked(self, info):
        return ProductLike.objects.filter(
            user=info.context.user, product__id=self.id, deleted=False
        ).exists()

    def resolve_brand(self, info):
        return self.brand

    def resolve_materials(self, info):
        return self.materials.all()

    def resolve_price(self, info):
        return format_price(self.price)


class CategoryType(graphene.ObjectType):
    id = graphene.Int()
    name = graphene.String()


class SubCategoryType(graphene.ObjectType):
    id = graphene.Int()
    name = graphene.String()


class CategoryTypes(DjangoObjectType):
    has_children = graphene.Boolean()
    full_path = graphene.String()

    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "parent",
            "children",
        )

    def resolve_full_path(self, info):
        return self.get_full_path()

    def resolve_has_children(self, info):
        if hasattr(self, "children_count"):
            return self.children_count > 0
        # Fallback if annotation isn't available
        return self.children.exists()


class SizeType(graphene.ObjectType):
    id = graphene.Int()
    name = graphene.String()


class BrandType(graphene.ObjectType):
    id = graphene.Int()
    name = graphene.String()


class LikedProductType(graphene.ObjectType):
    product = graphene.Field(ProductType)


class CategoryGroupType(graphene.ObjectType):
    id = graphene.Int()
    name = graphene.String()
    count = graphene.Int()


class BannerType(graphene.ObjectType):
    id = graphene.Int()
    title = graphene.String()
    season = graphene.String()
    banner_url = graphene.List(graphene.String)
    is_active = graphene.Boolean()


class RecommendedSellerType(graphene.ObjectType):
    seller = graphene.Field(UserType)
    total_sales = graphene.Decimal()
    total_shop_value = graphene.Decimal()
    product_views = graphene.Int()
    seller_score = graphene.Float()
    active_listings = graphene.Int()

    @classmethod
    def get_queryset(cls, queryset, info):
        """
        Annotates and filters a product queryset with various metrics for sellers.

        Args:
            cls: The class that this method is called on.
            queryset: The initial queryset of products.
            info: Additional information (not used in this method).

        Returns:
            QuerySet: A queryset annotated with the following fields:
                - seller__id: The ID of the seller.
                - seller__username: The username of the seller.
                - total_sales: The total sales amount for delivered orders in the last 30 days.
                - total_shop_value: The total value of active, non-deleted products.
                - product_views: The count of product views in the last 30 days.
                - active_listings: The count of active, non-deleted product listings.
                - seller_score: A composite score for the seller based on sales, shop value, and product views.

        The queryset is filtered to include only sellers with active listings and is ordered by seller_score in descending order.
        """
        recent_date = timezone.now() - timedelta(days=30)

        base_queryset = queryset.values("seller__id", "seller__username").annotate(
            # Total sales from delivered orders in last 30 days
            total_sales=Coalesce(
                Sum(
                    Case(
                        When(
                            orderitem__order__status=OrderStatusChoices.DELIVERED,
                            orderitem__order__created_at__gte=recent_date,
                            then=F("orderitem__price_at_purchase"),
                        ),
                        default=Value(Decimal("0.00")),
                        output_field=DecimalField(max_digits=10, decimal_places=2),
                    )
                ),
                Value(Decimal("0.00")),
                output_field=DecimalField(max_digits=10, decimal_places=2),
            ),
            # Total value of active products
            total_shop_value=Coalesce(
                Sum(
                    F("price"),
                    distinct=True,
                ),
                Value(Decimal("0.00")),
                output_field=DecimalField(max_digits=10, decimal_places=2),
            ),
            product_views=Coalesce(
                Count(
                    "productview",
                    filter=Q(productview__created_at__gte=recent_date),
                    distinct=True,
                ),
                Value(0),
                output_field=IntegerField(),
            ),
            active_listings=Count("id", distinct=True),
        )

        scored_queryset = (
            base_queryset.annotate(
                seller_score=ExpressionWrapper(
                    F("total_sales") * Value(Decimal("0.50"))
                    + F("total_shop_value") * Value(Decimal("0.30"))
                    + Cast(
                        F("product_views"),
                        DecimalField(max_digits=10, decimal_places=2),
                    )
                    * Value(Decimal("0.20")),
                    output_field=DecimalField(max_digits=10, decimal_places=2),
                )
            )
            .filter(active_listings__gt=0)
            .order_by("-seller_score")[:20]
        )

        return scored_queryset

    def resolve_total_sales(parent, info):
        return parent.get("total_sales") or Decimal("0.00")

    def resolve_total_shop_value(parent, info):
        return parent.get("total_shop_value") or Decimal("0.00")

    def resolve_product_views(parent, info):
        return parent.get("product_views") or 0

    def resolve_seller_score(parent, info):
        return parent.get("seller_score") or Decimal("0.00")

    def resolve_active_listings(parent, info):
        return parent.get("active_listings") or 0

    def resolve_seller(parent, info):
        seller_id = parent.get("seller__id")
        return User.objects.get(id=seller_id)
