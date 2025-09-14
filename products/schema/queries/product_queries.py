import re
import graphene
from products.choices import SizeSubTypeChoices, SizeTypeChoices, StatusChoices
from products.models import (
    Banner,
    Brand,
    Category,
    Material,
    Product,
    ProductLike,
    RecentlyViewedProduct,
    Size,
)
from products.schema.api_descriptions import (
    ALL_PRODUCTS,
    PRODUCT,
    RECOMMENDED_SELLERS,
    USER_PRODUCT_GROUPING,
    USER_PRODUCTS,
)
from products.schema.enums.product_enums import ProductGroupingEnum, SortEnum
from products.schema.inputs.product_inputs import ProductFiltersInput, OrderFiltersInput
from products.schema.types.product_types import (
    BannerType,
    BrandType,
    CategoryGroupType,
    CategoryTypes,
    LikedProductType,
    ProductType,
    RecommendedSellerType,
    SizeType,
)
from utils.decorators import cache_categories, cache_sizes
from utils.non_modular_utils.database_utils import DatabaseUtil
from utils.product_utils.product_utils import ProductUtils
from graphql_jwt.decorators import login_required
from django.db.models import Count, Q
from utils.utils import get_exclusion_queries


class Query(graphene.ObjectType):
    pagination_result = None

    all_products = graphene.List(
        ProductType,
        filters=graphene.Argument(ProductFiltersInput),
        sort=SortEnum(),
        search=graphene.String(),
        page_count=graphene.Int(),
        page_number=graphene.Int(),
        description=ALL_PRODUCTS,
    )

    product = graphene.Field(
        ProductType,
        id=graphene.Int(required=True),
        description=PRODUCT,
    )

    liked_products = graphene.List(
        LikedProductType,
        page_count=graphene.Int(),
        page_number=graphene.Int(),
    )

    categories = graphene.List(CategoryTypes, parent_id=graphene.Int())
    sizes = graphene.List(SizeType, path=graphene.String(required=True))
    brands = graphene.List(
        BrandType,
        search=graphene.String(),
        page_count=graphene.Int(),
        page_number=graphene.Int(),
    )
    # popular_brands = graphene.List(BrandType, top=graphene.Int(required=True))
    materials = graphene.List(
        BrandType,
        search=graphene.String(),
        page_count=graphene.Int(),
        page_number=graphene.Int(),
    )
    similar_products = graphene.List(
        ProductType,
        product_id=graphene.Int(),
        category_id=graphene.Int(),
        page_count=graphene.Int(),
        page_number=graphene.Int(),
    )
    recommend_products = graphene.List(
        ProductType, page_count=graphene.Int(), page_number=graphene.Int()
    )
    recently_viewed_products = graphene.List(
        ProductType,
    )
    # favorite_brand_products = graphene.List(
    #     ProductType, top=graphene.Int(required=True)
    # )

    all_products_total_number = graphene.Int()
    # brands_total_number = graphene.Int()
    # liked_products_total_number = graphene.Int()
    # materials_total_number = graphene.Int()
    # similar_products_total_number = graphene.Int()
    # recommended_sellers_total_number = graphene.Int()
    # recommend_products_total_number = graphene.Int()

    # @login_required
    def resolve_all_products(self, info, **kwargs):
        page_count = kwargs.get("page_count", None)
        page_number = kwargs.get("page_number", None)
        user = info.context.user if info.context.user.is_authenticated else None

        try:
            products = ProductUtils.resolve_all_products(user, **kwargs)
            
            # Ensure products is not None
            if products is None:
                products = Product.objects.none()

            # Paginate result
            result, total_pages, total_items = DatabaseUtil.paginate_query(
                products, page_count, page_number
            )
            Query.pagination_result = (result, total_pages, total_items)

            # Ensure we always return a list, never None
            return result if result is not None else []
            
        except Exception as e:
            # Log the error and return empty list
            print(f"Error in resolve_all_products: {e}")
            Query.pagination_result = ([], 0, 0)
            return []

    def resolve_all_products_total_number(self, info, **kwargs):
        if not Query.pagination_result:
            return 0
        return Query.pagination_result[2]

    @login_required
    def resolve_user_products(self, info, **kwargs):
        page_count = kwargs.get("page_count", None)
        page_number = kwargs.get("page_number", None)

        products = ProductUtils.resolve_user_products(info.context.user, **kwargs)

        # Paginate result
        result, total_pages, total_items = DatabaseUtil.paginate_query(
            products, page_count, page_number
        )
        Query.pagination_result = (result, total_pages, total_items)

        return result

    def resolve_product(self, info, **kwargs):
        product_id = kwargs.get("id")
        
        # Allow viewing products without authentication
        user = info.context.user if info.context.user.is_authenticated else None
        product = ProductUtils.resolve_product(user, product_id)

        return product

    @login_required
    # @cache_categories(timeout=None)  # TODO: Change to indefinite cache - temporarily disabled for debugging
    def resolve_categories(self, info, **kwargs):
        parent_id = kwargs.get("parent_id", None)

        queryset = Category.objects.annotate(children_count=Count("children"))

        # Filter based on parent_id
        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)
        else:
            queryset = queryset.filter(parent__isnull=True)

        return queryset.order_by("name")

    @login_required
    @cache_sizes(timeout=None)
    def resolve_sizes(
        self, info, **kwargs
    ):  # TODO: Might need to refactor this resolve function
        path = kwargs.get("path")
        path = re.sub(
            r"(?i)^(Boys|Girls)( > |$)", r"Kids\2", path
        )  # This approach works for replacing the first occurrence of "Boys" or "Girls" in the path with "Kids"

        if not path or len(path.split(" > ")) < 2:
            return []

        path = path.split(" > ")[:2]

        print("cache miss", path)
        try:
            if "Accessories" in path:
                size_type = SizeTypeChoices.UNISEX
                size_subtype = SizeSubTypeChoices.ACCESSORIES
            else:
                size_type = SizeTypeChoices[path[0].upper()]
                size_subtype = SizeSubTypeChoices[path[1].upper()]
        except KeyError:
            return []

        sizes = Size.objects.filter(
            size_type=size_type,
            size_subtype=size_subtype,
        ).only(
            "id",
            "name",
        )

        return sizes

    # @login_required
    def resolve_brands(self, info, **kwargs):
        search_query = kwargs.get("search", None)
        page_count = kwargs.get("page_count", None)
        page_number = kwargs.get("page_number", None)

        brands = Brand.objects.all()

        if search_query:
            brands = brands.filter(name__istartswith=search_query)

        # Paginate result
        result, total_pages, total_items = DatabaseUtil.paginate_query(
            brands, page_count, page_number
        )
        Query.pagination_result = (result, total_pages, total_items)

        return result

    @login_required
    def resolve_popular_brands(self, info, **kwargs):
        top = kwargs.get("top")
        return Brand.objects.annotate(products_count=Count("product")).order_by(
            "-products_count"
        )[:top]

    def resolve_brands_total_number(self, info, **kwargs):
        if not Query.pagination_result:
            return 0
        return Query.pagination_result[2]

    @login_required
    def resolve_materials(self, info, **kwargs):
        search_query = kwargs.get("search", None)
        page_count = kwargs.get("page_count", None)
        page_number = kwargs.get("page_number", None)

        materials = Material.objects.all()

        if search_query:
            materials = materials.filter(name__icontains=search_query)

        # Paginate result
        result, total_pages, total_items = DatabaseUtil.paginate_query(
            materials, page_count, page_number
        )
        Query.pagination_result = (result, total_pages, total_items)

        return result

    @login_required
    def resolve_materials_total_number(self, info, **kwargs):
        if not Query.pagination_result:
            return 0
        return Query.pagination_result[2]

    @login_required
    def resolve_liked_products(self, info, **kwargs):
        page_count = kwargs.get("page_count", None)
        page_number = kwargs.get("page_number", None)

        exclusion_conditions = get_exclusion_queries()

        liked_products = ProductLike.objects.filter(user=info.context.user).exclude(
            Q(exclusion_conditions) | Q(deleted=True)
        )

        # Paginate result
        result, total_pages, total_items = DatabaseUtil.paginate_query(
            liked_products, page_count, page_number
        )
        Query.pagination_result = (result, total_pages, total_items)
        return result

    @login_required
    def resolve_liked_products_total_number(self, info, **kwargs):
        if not Query.pagination_result:
            return 0
        return Query.pagination_result[2]

    @login_required
    def resolve_similar_products(self, info, **kwargs):
        page_count = kwargs.get("page_count", None)
        page_number = kwargs.get("page_number", None)

        products = ProductUtils.resolve_similar_products(**kwargs)

        # Paginate result
        result, total_pages, total_items = DatabaseUtil.paginate_query(
            products, page_count, page_number
        )
        Query.pagination_result = (result, total_pages, total_items)

        return result

    @login_required
    def resolve_similar_products_total_number(self, info, **kwargs):
        if not Query.pagination_result:
            return 0
        return Query.pagination_result[2]

    @login_required
    def resolve_filter_products_by_price(self, info, **kwargs):
        price_limit = kwargs.get("price_limit")
        page_count = kwargs.get("page_count", None)
        page_number = kwargs.get("page_number", None)

        products = Product.objects.filter(price__lte=price_limit).exclude(deleted=True)
        # Paginate result
        result, total_pages, total_items = DatabaseUtil.paginate_query(
            products, page_count, page_number
        )
        Query.pagination_result = (result, total_pages, total_items)

        return result

    @login_required
    def resolve_filter_products_by_price_total_number(self, info, **kwargs):
        if not Query.pagination_result:
            return 0
        return Query.pagination_result[2]

    @login_required
    def resolve_user_product_grouping(self, info, **kwargs):
        user_id = kwargs.get("user_id")
        group_by = kwargs.get("group_by")

        return ProductUtils.user_product_grouping(user_id, group_by)

    @login_required
    def resolve_recently_viewed_products(self, info, **kwargs):
        # Get recently viewed products with timestamps
        recently_viewed = (
            RecentlyViewedProduct.objects.filter(user=info.context.user)
            .select_related("product")
            .order_by("-viewed_at")[:20]
        )

        # Extract products while maintaining order
        products = [rv.product for rv in recently_viewed]

        return products

    @login_required
    def resolve_banner(self, info):
        return Banner.objects.filter(is_active=True).first()

    @login_required
    def resolve_recommended_sellers(self, info, **kwargs):
        page_count = kwargs.get("page_count", None)
        page_number = kwargs.get("page_number", None)
        # Query the Product model to aggregate sellers' performance
        queryset = Product.objects.filter(status=StatusChoices.ACTIVE, deleted=False)

        # Call get_queryset on Product model
        recommended_seller = RecommendedSellerType.get_queryset(queryset, info)

        # Paginate result
        result, total_pages, total_items = DatabaseUtil.paginate_query(
            recommended_seller, page_count, page_number
        )
        Query.pagination_result = (result, total_pages, total_items)

        return result

    @login_required
    def resolve_recommended_sellers_total_number(self, info, **kwargs):
        if not Query.pagination_result:
            return 0
        return Query.pagination_result[2]

    @login_required
    def resolve_recommend_products(self, info, **kwargs):

        page_count = kwargs.get("page_count", None)
        page_number = kwargs.get("page_number", None)

        products = ProductUtils.recommend_products(info.context.user)

        result, total_pages, total_items = DatabaseUtil.paginate_query(
            products, page_count, page_number
        )

        Query.pagination_result = (result, total_pages, total_items)

        return products

    @login_required
    def resolve_recommend_products_total_number(self, info, **kwargs):
        if not Query.pagination_result:
            return 0
        return Query.pagination_result[2]

    @login_required
    def resolve_favorite_brand_products(self, info, **kwargs):
        top = kwargs.get("top", 10)
        user = info.context.user

        return ProductUtils.favorite_brand_products(user, top)

    @login_required
    def resolve_user_orders(self, info, **kwargs):
        user = info.context.user
        page_count = kwargs.get("page_count", None)
        page_number = kwargs.get("page_number", None)

        orders = ProductUtils.user_orders(user, **kwargs)
        result, total_pages, total_items = DatabaseUtil.paginate_query(
            orders, page_count, page_number
        )
        Query.pagination_result = (result, total_pages, total_items)

        return result

    @login_required
    def resolve_user_orders_total_number(self, info, **kwargs):
        if not Query.pagination_result:
            return 0
        return Query.pagination_result[2]
