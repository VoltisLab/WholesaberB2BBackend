import re
import logging
import requests
from io import BytesIO
from decimal import Decimal
from typing import List, Optional
from PIL import Image
from django.conf import settings
from accounts.models import User
from notifications.schema.mutations.notification_mutations import CreateNotification
from products.choices import StatusChoices

from products.models import (
    Brand,
    Category,
    Material,
    Product,
    ProductLike,
    ProductView,
    RecentlyViewedProduct,
    Size,
)
from products.schema.enums.product_enums import (
    ImageActionEnum,
    ProductGroupingEnum,
    ProductFlagReasonEnum,
    ProductFlagTypeEnum,
)
from products.schema.product_responses import (
    PRODUCT_DELETE_ERROR,
    PRODUCT_NOT_FOUND,
    PRODUCT_FEATURED_MAXIMUM_REACHED,
    MINIMUM_PRODUCT_REQUIRED,
)
from products.schema.types.product_types import CategoryGroupType
from utils.non_modular_utils.errors import ErrorException, GenericError, StandardError
from django.db import transaction
from django.db.models import (
    Q,
    Count,
    F,
    Case,
    When,
    Value,
    CharField,
)
from django.db.models.functions import Coalesce, Greatest, Concat, Substr, StrIndex
from utils.upload_utils import UploadUtil
from utils.utils import (
    build_product_filter_conditions,
    format_datetime,
    get_exclusion_queries,
    build_order_filter_conditions,
    get_template_path,
    get_cold_start_brands,
)
from datetime import timedelta
from django.utils import timezone

logger = logging.getLogger(__name__)


class ProductUtils:
    @staticmethod
    def create_product(logged_in_user: User, **kwargs: dict) -> Product:
        category_id = kwargs.get("category")
        size_id = kwargs.get("size", None)
        brand_id = kwargs.get("brand", None)
        material_ids = kwargs.get("materials", None)
        parcel_size = (
            kwargs.get("parcel_size").value if kwargs.get("parcel_size") else None
        )
        condition = kwargs.get("condition").value if kwargs.get("condition") else None
        style = kwargs.get("style").value if kwargs.get("style") else None
        hashtags = re.findall(r"#\w+", kwargs.get("description"))
        try:
 
            # Related instances
            category = Category.objects.get(id=category_id)
            if size_id:
                size = Size.objects.get(id=size_id)
            if brand_id:
                brand = Brand.objects.get(id=brand_id)
            if material_ids:
                materials = Material.objects.filter(id__in=material_ids)

            data = {
                "name": kwargs.get("name"),
                "seller": logged_in_user,
                "description": kwargs.get("description"),
                "price": kwargs.get("price"),
                "discount_price": kwargs.get("discount", Decimal(0.00)),
                "condition": condition,
                "parcel_size": parcel_size,
                "size": size if size_id else None,
                "style": style,
                "category": category,
                "images_url": kwargs.get("images_url"),
                "color": kwargs.get("color"),
                "brand": brand if brand_id else None,
                "custom_brand": kwargs.get("custom_brand"),
                "color": kwargs.get("color"),
                "hashtags": hashtags,
                # "status": StatusChoices.INACTIVE,
            }

            product = Product.objects.create(**data)
            if material_ids:
                product.materials.set(materials)

            # Run product upload checks asynchronously
            # run_product_upload_checks.delay(product.id)

            return product

        except (
            Category.DoesNotExist,
            Size.DoesNotExist,
        ) as e:
            raise ErrorException(
                message=str(e),
                error_type=GenericError,
                meta={},
                code=422,
            )

        except Exception as e:
            raise ErrorException(
                message=f"An error occurred while creating the product. {e}",
                error_type=GenericError,
                meta={},
                code=422,
            )

    @staticmethod
    def duplicate_product(logged_in_user: User, product_id: int, **kwargs: dict) -> Product:
        """
        Duplicate an existing product with optional modifications.
        
        Args:
            logged_in_user: The user creating the duplicate
            product_id: ID of the product to duplicate
            **kwargs: Optional modifications to apply to the duplicate
            
        Returns:
            Product: The newly created duplicate product
        """
        try:
            # Get the original product
            original_product = Product.objects.get(id=product_id, deleted=False)
            
            # Create the duplicate with modified data
            duplicate_data = {
                "name": kwargs.get("name", f"{original_product.name} (Copy)"),
                "seller": logged_in_user,
                "description": kwargs.get("description", original_product.description),
                "price": kwargs.get("price", original_product.price),
                "discount_price": kwargs.get("discount_price", original_product.discount_price),
                "condition": kwargs.get("condition", original_product.condition),
                "parcel_size": kwargs.get("parcel_size", original_product.parcel_size),
                "size": kwargs.get("size", original_product.size),
                "style": kwargs.get("style", original_product.style),
                "category": kwargs.get("category", original_product.category),
                "images_url": kwargs.get("images_url", original_product.images_url),
                "color": kwargs.get("color", original_product.color),
                "brand": kwargs.get("brand", original_product.brand),
                "custom_brand": kwargs.get("custom_brand", original_product.custom_brand),
                "hashtags": kwargs.get("hashtags", original_product.hashtags),
                "is_featured": False,  # New products are not featured by default
                "status": StatusChoices.ACTIVE,
            }
            
            # Create the duplicate product
            duplicate_product = Product.objects.create(**duplicate_data)
            
            # Copy materials if they exist
            if original_product.materials.exists():
                duplicate_product.materials.set(original_product.materials.all())
            
            return duplicate_product
            
        except Product.DoesNotExist:
            raise ErrorException(
                message="Product not found",
                error_type=GenericError,
                meta={"product_id": product_id},
                code=404,
            )
        except Exception as e:
            raise ErrorException(
                message=f"Failed to duplicate product: {str(e)}",
                error_type=GenericError,
                meta={"product_id": product_id},
                code=500,
            )

    @staticmethod
    def update_product(logged_in_user: User, **kwargs: dict) -> Product:
        try:
            materials = None
            product_id = kwargs.get("product_id")
            instance = Product.objects.get(id=product_id, seller=logged_in_user)

            # Fetch related instances if needed
            if "category" in kwargs:
                category = Category.objects.get(id=kwargs.pop("category"))
                kwargs["category"] = category

            if "size" in kwargs:
                size = Size.objects.get(id=kwargs.pop("size"))
                kwargs["size"] = size

            if "brand" in kwargs:
                brand = Brand.objects.get(id=kwargs.pop("brand"))
                kwargs["brand"] = brand

            if "materials" in kwargs:
                material_ids = kwargs.pop("materials")
                materials = Material.objects.filter(
                    id__in=material_ids
                )  # Fetch materials by IDs

            if "images_url" in kwargs:
                current_banners = instance.images_url
                images_to_modify = kwargs["images_url"]["images"]
                action = kwargs["images_url"]["action"]

                new_banners = ProductUtils.update_banner_urls(
                    current_banners, images_to_modify, action
                )
                kwargs["images_url"] = new_banners

            if "style" in kwargs:
                kwargs["style"] = kwargs["style"].value
            if "condition" in kwargs:
                kwargs["condition"] = kwargs["condition"].value
            if "parcel_size" in kwargs:
                kwargs["parcel_size"] = kwargs["parcel_size"].value

            if "is_featured" in kwargs and kwargs["is_featured"]:
                MIN_NUMBER_OF_PRODUCTS = 5
                MAX_NUMBER_OF_FEATURABLE_PRODUCTS_FOR_USER = 5

                seller_product_count = Product.objects.filter(
                    seller=logged_in_user, deleted=False
                ).count()

                if seller_product_count < MIN_NUMBER_OF_PRODUCTS:
                    raise ErrorException(
                        message=MINIMUM_PRODUCT_REQUIRED.format(MIN_NUMBER_OF_PRODUCTS),
                        error_type=StandardError,
                        meta={},
                        code=400,
                    )

                featured_product_count = Product.objects.filter(
                    seller=logged_in_user,
                    is_featured=True,
                    status=StatusChoices.ACTIVE.value,
                ).count()
                if featured_product_count >= MAX_NUMBER_OF_FEATURABLE_PRODUCTS_FOR_USER:
                    raise ErrorException(
                        message=PRODUCT_FEATURED_MAXIMUM_REACHED.format(
                            MAX_NUMBER_OF_FEATURABLE_PRODUCTS_FOR_USER
                        ),
                        error_type=StandardError,
                        meta={},
                        code=400,
                    )

            # Update product instance
            for key, value in kwargs.items():
                setattr(instance, key, value)
            instance.save()
            # Update the materials field
            if materials:
                instance.materials.set(materials)

            return instance

        except Product.DoesNotExist:
            raise ErrorException(
                message=PRODUCT_NOT_FOUND.format(product_id),
                error_type=StandardError,
                meta={},
                code=404,
            )
        except (
            Category.DoesNotExist,
            Size.DoesNotExist,
        ) as e:
            raise ErrorException(
                message=str(e),
                error_type=GenericError,
                meta={},
                code=422,
            )
        except Exception as e:
            raise ErrorException(
                message=f"An error occurred while updating the product. {e}",
                error_type=GenericError,
                meta={},
                code=422,
            )

    @staticmethod
    def update_banner_urls(
        current_banners: list,
        new_banners: list,
        action: ImageActionEnum,
        max_banners=None,
    ) -> list:
        if action == ImageActionEnum.ADD:
            if not new_banners:
                raise ValueError(
                    "At least one new banner must be provided for ADD action."
                )

            # Check if any of the new banners already exist in the current banners
            for banner in new_banners:
                if banner in current_banners:
                    raise ValueError(f"Banner URL {banner['url']} already exists.")

            # Check size limit (assuming max allowed banners is 3)
            if max_banners:
                if len(current_banners) + len(new_banners) > 3:
                    raise ValueError("Maximum banner limit reached.")

            # Add the new banners
            current_banners.extend(new_banners)
            return current_banners

        elif action == ImageActionEnum.REMOVE:
            if not current_banners:
                raise ValueError("No banners to remove.")

            updated_banners = [url for url in current_banners if url not in new_banners]

            # Call UploadUtil to delete all existing banners from S3
            urls_to_delete = [banner["url"] for banner in new_banners]
            UploadUtil.delete_file(urls_to_delete, settings.PRODUCT)
            return updated_banners

        elif action == ImageActionEnum.UPDATE_INDEX:
            return new_banners

        else:
            raise ValueError("Invalid action. Action must be 'ADD' or 'REMOVE'.")

    @staticmethod
    def delete_product(logged_in_user: User, product_id: int) -> None:
        try:
            instance = Product.objects.filter(id=product_id, seller=logged_in_user)
            if not instance:
                raise ErrorException(
                    message=PRODUCT_NOT_FOUND.format(product_id),
                    error_type=StandardError,
                    meta={},
                    code=404,
                )

            instance.update(deleted=True)

        except Exception as err:
            raise ErrorException(
                message=PRODUCT_DELETE_ERROR.format(err),
                error_type=GenericError,
                meta={},
                code=422,
            )

    @staticmethod
    def like_product(logged_in_user: User, product_id: int) -> None:
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise ErrorException(
                message=PRODUCT_NOT_FOUND.format(product_id),
                error_type=StandardError,
                meta={},
                code=404,
            )

        # Using a transaction to ensure atomicity
        with transaction.atomic():
            product_like, created = ProductLike.objects.get_or_create(
                product=product, user=logged_in_user
            )

            if created or product_like.deleted:
                # New like, increment the count
                product_like.deleted = False
                product.likes += 1
                success = True

                if logged_in_user != product.seller:
                    # Notify the seller of the like
                    if created or product_like.deleted:
                        media_thumbnail = (
                            product.images_url[0] if product.images_url else ""
                        )

                        CreateNotification.create_notification.delay(
                            user_id=product.seller.id,
                            sender=logged_in_user.id,
                            message="liked your product",
                            model="Product",
                            model_id=product.id,
                            model_group="Product",
                            title=logged_in_user.username,
                            meta={"media_thumbnail": media_thumbnail},
                            info={"page": "PRODUCT", "object_id": str(product.id)},
                        )
            else:
                # Unlike the product, delete the existing like
                product_like.deleted = True
                product.likes = max(product.likes - 1, 0)
                success = False

            # Save the updated product object
            product.save()
            product_like.save()
            return success

    @staticmethod
    def resolve_all_products(loggedin_user, **kwargs: dict) -> List[Product]:
        try:
            search = kwargs.get("search", None)
            filters = kwargs.get("filters", {})
            sort = kwargs.get("sort", None)

            # Build filter conditions using the helper function
            filter_conditions = build_product_filter_conditions(
                loggedin_user, filters, search
            )
            exclusion_conditions = get_exclusion_queries("seller")

            # Add a filter to include only active products
            filter_conditions &= Q(status=StatusChoices.ACTIVE)

            # Apply all filters in one query
            if sort:
                products = Product.objects.filter(filter_conditions).order_by(sort.value)
            else:
                products = Product.objects.filter(filter_conditions).order_by("?")

            result = products.exclude(exclusion_conditions)
            
            # Ensure we return a QuerySet, not None
            return result if result is not None else Product.objects.none()
            
        except Exception as e:
            print(f"Error in ProductUtils.resolve_all_products: {e}")
            # Return empty queryset instead of None
            return Product.objects.none()

    @staticmethod
    def resolve_user_products(logged_in_user: User, **kwargs: dict) -> List[Product]:
        search = kwargs.get("search", None)
        username = kwargs.get("username", None)
        filters = kwargs.get("filters", {})
        sort = kwargs.get("sort", None)

        if username:
            products = Product.objects.filter(
                seller__username=username, status=StatusChoices.ACTIVE
            )
        else:
            products = Product.objects.filter(seller=logged_in_user)

        # Build filter conditions using the helper function
        filter_conditions = build_product_filter_conditions(
            logged_in_user, filters, search
        )
        exclusion_conditions = get_exclusion_queries("seller")

        # Apply sorting if a sort field is provided
        if sort:
            products = products.filter(filter_conditions).order_by(sort.value)
        else:
            products = products.filter(filter_conditions).order_by("?")

        return products.exclude(exclusion_conditions)

    @staticmethod
    def resolve_product(logged_in_user, product_id: int) -> Product:
        exclusion_conditions = get_exclusion_queries("seller")
        try:
            product = Product.objects.exclude(exclusion_conditions).get(
                id=product_id, deleted=False
            )

            # Only update view count if user is logged in and not the seller
            if logged_in_user and product.seller != logged_in_user:
                # Using select_for_update to prevent race conditions on views count
                with transaction.atomic():
                    product = Product.objects.select_for_update().get(id=product_id)

                    # Update view and increment counter
                    _, created = ProductView.objects.update_or_create(
                        product=product,
                        viewed_by=logged_in_user,
                        defaults={"created_at": timezone.now()},
                    )

                    if created:
                        Product.objects.filter(id=product_id).update(
                            views=F("views") + 1
                        )


            return product
        except Product.DoesNotExist:
            raise ErrorException(
                message="Product does not exist.",
                error_type=GenericError,
                meta={},
                code=422,
            )
        except Exception as e:
            raise ErrorException(
                message=f"An error occurred while retrieving the product {e}.",
                error_type=GenericError,
                meta={},
                code=422,
            )

    @staticmethod
    def user_product_grouping(user_id: int, group_by: str) -> List[CategoryGroupType]:
        MIN_GROUPABLE_PRODUCTS_CATEGORY = 3
        MIN_GROUPABLE_PRODUCTS_BRAND = 5

        if group_by == ProductGroupingEnum.CATEGORY:
            duplicate_categories = (
                Product.objects.filter(seller__id=user_id)
                .exclude(deleted=True)
                .values("category__name")
                .annotate(root_count=Count("category__slug", distinct=True))
                .filter(root_count__gt=1)
                .values_list("category__name", flat=True)
            )

            groups = (
                Product.objects.filter(seller__id=user_id)
                .exclude(Q(deleted=True) | Q(status=StatusChoices.SOLD))
                .values(
                    "category__id",
                    "category__name",
                    "category__slug",
                )
                .annotate(
                    root_category=Substr(
                        "category__slug", 1, StrIndex("category__slug", Value("-")) - 1
                    ),
                    full_category_name=Case(
                        When(
                            category__name__in=duplicate_categories,
                            then=Concat(
                                "root_category",
                                Value(" - "),
                                "category__name",
                                output_field=CharField(),
                            ),
                        ),
                        default="category__name",
                        output_field=CharField(),
                    ),
                    product_count=Count("id"),
                )
                .order_by("full_category_name")
            )
            if len(groups) < MIN_GROUPABLE_PRODUCTS_CATEGORY:
                return []
            label = "full_category_name"
            id_label = "category__id"
        elif group_by == ProductGroupingEnum.BRAND:
            groups = (
                Product.objects.filter(seller__id=user_id, brand__isnull=False)
                .exclude(Q(deleted=True) | Q(status=StatusChoices.SOLD))
                .values("brand__id", "brand__name")
                .annotate(product_count=Count("id"))
                .order_by("brand__name")
            )
            if len(groups) < MIN_GROUPABLE_PRODUCTS_BRAND:
                return []
            label = "brand__name"
            id_label = "brand__id"

        elif group_by == ProductGroupingEnum.TOP_BRAND:
            # Find the top brands based on the number of products
            groups = (
                Product.objects.filter(seller__id=user_id, brand__isnull=False)
                .exclude(Q(deleted=True) | Q(status=StatusChoices.SOLD))
                .values("brand__id", "brand__name")
                .annotate(product_count=Count("id"))
                .order_by("-product_count")[:10]
            )
            if len(groups) < MIN_GROUPABLE_PRODUCTS_BRAND:
                return []
            label = "brand__name"
            id_label = "brand__id"

        else:
            raise ErrorException(
                message="Invalid grouping parameter.",
                error_type=GenericError,
                meta={},
                code=400,
            )

        return [
            CategoryGroupType(
                id=int(i[id_label]),
                name=str(i[label]).title(),
                count=int(i["product_count"]),
            )
            for i in groups
        ]

    @staticmethod
    def resolve_similar_products(**kwargs):
        product_id = kwargs.get("product_id", None)
        category_id = kwargs.get("category_id", None)
        exclusion_conditions = get_exclusion_queries("seller")

        if product_id:
            try:
                product = Product.objects.exclude(exclusion_conditions).get(
                    id=product_id, deleted=False
                )
                query = Q()
                if product.brand:
                    query &= Q(brand=product.brand, status=StatusChoices.ACTIVE)
                else:
                    query &= Q(
                        custom_brand__icontains=product.custom_brand,
                        status=StatusChoices.ACTIVE,
                    )

                # Find similar products by brand or brand, excluding the current product
                similar_products = (
                    Product.objects.filter(query)
                    .exclude(Q(id=product_id) | Q(deleted=True))
                    .order_by("price")
                )

            except Product.DoesNotExist:
                raise ErrorException(
                    message=PRODUCT_NOT_FOUND.format(product_id),
                    error_type=GenericError,
                    meta={},
                    code=404,
                )

        elif category_id:
            similar_products = (
                Product.objects.filter(
                    category__id=category_id,
                    status=StatusChoices.ACTIVE,
                )
                .exclude(deleted=True)
                .order_by("price")
            )

        else:
            raise ErrorException(
                message="Category ID is required.",
                error_type=GenericError,
                meta={},
                code=400,
            )

        return similar_products


    @staticmethod
    def recommend_products(user):

        user_recently_viewed_products = RecentlyViewedProduct.objects.filter(user=user)
        user_liked_products = ProductLike.objects.filter(user=user, deleted=False)

        category_ids = set(
            user_recently_viewed_products.values_list(
                "product__category__id", flat=True
            )
        ) | set(user_liked_products.values_list("product__category_id", flat=True))
        brand_ids = set(
            user_recently_viewed_products.values_list("product__brand__id", flat=True)
        ) | set(user_liked_products.values_list("product__brand_id", flat=True))

        products = (
            Product.objects.filter(
                Q(category_id__in=category_ids) | Q(brand_id__in=brand_ids)
            )
            .distinct()
            .order_by("-created_at")
            .exclude(deleted=True)
        )

        if not products.exists():
            return Product.objects.filter(deleted=False)
        return products

    @staticmethod
    def favorite_brand_products(user: User, top: int) -> Optional[List[Product]]:
        MIN_LIKED_PRODUCTS = 2

        user_liked_products = ProductLike.objects.filter(user=user, deleted=False)

        if user_liked_products.count() >= MIN_LIKED_PRODUCTS:
            cold_start_brands = get_cold_start_brands(user.id)
            brand_ids = cold_start_brands["brand_ids"]

            products = (
                Product.objects.filter(brand__id__in=brand_ids)
                .exclude(Q(get_exclusion_queries("seller")) | Q(deleted=True))
                .order_by("-created_at")[:top]
            )
            return products

        return []