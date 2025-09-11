import random
import os
import uuid
import pytz
from django.conf import settings
from django.db.models import Q
from datetime import datetime, timezone
from accounts.models import User
from accounts.schema.enums.accounts_enums import SearchTypeEnum
from products.choices import StatusChoices
from products.models import Category, Product
from products.schema.enums.product_enums import ClientOrderStatusEnum, OrderStatusEnum
from utils.search_utils.search_utils import SearchUtils
from typing import List, Optional
from asgiref.sync import async_to_sync
from itertools import chain

from django.core.exceptions import ValidationError
from typing import Dict, List, Optional


def get_template_path(template_name: str, sub_directory: str = None) -> str:
    """
    Construct the full file path to a template based on the provided template name
    and an optional sub-directory.

    This function ensures that the template name has the `.html` extension. If the
    `sub_directory` is provided, the function will include it in the path. If `sub_directory`
    is not specified, the function will default to a predefined base directory for templates.

    Args:
        template_name (str): The name of the template file. If it does not
                             already end with `.html`, the function will append
                             this extension.
        sub_directory (str, optional): The name of a sub-directory within the
                                        templates directory. If provided, the
                                        full path will include this sub-directory.
                                        If not provided, the base directory will be
                                        used instead.

    Returns:
        str: The full file path to the specified template.

    Raises:
        ValueError: If the template_name is an empty string.

    Example:
        >>> get_template_path("my_template", "notifications")
        '/path/to/your/project/templates/email/notifications/my_template.html'

        >>> get_template_path("my_template")
        '/path/to/your/project/templates/email/my_template.html'
    """
    # Ensure template_name has .html extension
    if not template_name.endswith(".html"):
        template_name = f"{template_name}.html"

    # Base directory for templates
    base_directory = "email"

    if sub_directory:
        full_path = os.path.join(
            settings.BASE_DIR, "templates", base_directory, sub_directory, template_name
        )
    else:
        full_path = os.path.join(
            settings.BASE_DIR, "templates", base_directory, template_name
        )

    return full_path


def format_price(price):
    """
    Format the price to an integer if it has no decimal value,
    otherwise return it with two decimal places.
    """
    price = float(price)

    if price.is_integer():
        return int(price)
    return round(price, 2)


def truncate_metadata(metadata_value: str, max_length=500) -> str:
    """
    Truncates the provided metadata value to ensure it does not exceed the specified maximum length.

    Args:
        metadata_value (str): The metadata value to be truncated.
        max_length (int): The maximum allowed length for the metadata value. Default is 500.

    Returns:
        str: The truncated metadata value if it exceeds the max_length; otherwise, returns the original metadata value.
    """
    if len(metadata_value) > max_length:
        return metadata_value[:max_length]
    return metadata_value


def milli_date():
    date = datetime.now(timezone.utc) - datetime(1970, 1, 1, tzinfo=timezone.utc)

    # Get the total seconds since the epoch and convert to milliseconds
    milliseconds = round(date.total_seconds() * 1000)

    return milliseconds


def generate_reference():
    return f"PRELURA-{uuid.uuid4()}-{milli_date()}".lower()


def build_product_filter_conditions(user: User, filters: dict, search: str = None) -> Q:
    # Initialize filter conditions with deleted=False to exclude deleted items
    filter_conditions = Q(deleted=False)

    # Apply filters dynamically
    if "name" in filters:
        filter_conditions &= Q(name__icontains=filters["name"])
    if "brand" in filters:
        filter_conditions &= Q(brand__id=filters["brand"])
    if "parent_category" in filters:
        child_categories_ids = Category.objects.filter(
            slug__startswith=filters["parent_category"].value.lower()
        ).values_list("id", flat=True)
        filter_conditions &= Q(category__in=child_categories_ids)
    if "category" in filters:
        filter_conditions &= Q(category__id=filters["category"])
    if "custom_brand" in filters:
        filter_conditions &= Q(custom_brand=filters["custom_brand"])
    # Price range filter
    if "min_price" in filters and "max_price" in filters:
        filter_conditions &= Q(
            price__gte=filters["min_price"], price__lte=filters["max_price"]
        )
    elif "min_price" in filters:
        filter_conditions &= Q(price__gte=filters["min_price"])
    elif "max_price" in filters:
        filter_conditions &= Q(price__lte=filters["max_price"])

    if "condition" in filters:
        filter_conditions &= Q(condition=filters["condition"].value)
    if "size" in filters:
        filter_conditions &= Q(size__id=filters["size"])
    if "style" in filters:
        filter_conditions &= Q(style=filters["style"].value)
    if "status" in filters:
        filter_conditions &= Q(status=filters["status"].value)
    if "discount_price" in filters and filters["discount_price"] is True:
        filter_conditions &= Q(discount_price__gt=0)
    if "hashtags" in filters:
        filter_conditions &= Q(
            id__in=get_product_ids_with_hashtags(filters["hashtags"])
        )
    if "colors" in filters:
        filter_conditions &= Q(color__contains=filters["colors"])

    # Add search term filter if provided
    if search:
        filter_conditions &= Q(name__icontains=search) | Q(
            brand__name__icontains=search
        )
        if user:
            SearchUtils.save_search_query(
                user=user, query=search, search_type=SearchTypeEnum.PRODUCT.value
            )

    return filter_conditions


def build_user_filter_conditions(filters: dict, search: str = None) -> Q:
    """User filter conditions"""
    filter_conditions = Q(
        is_active=True,
        deleted=False,
        is_banned=False,
        is_staff=False,
        is_superuser=False,
    )

    # Apply filters dynamically
    if "gender" in filters:
        filter_conditions &= Q(gender=filters["gender"].value)

    if "is_verified" in filters:
        filter_conditions &= Q(status__verified=filters["is_verified"])

    if "country" in filters:
        filter_conditions &= Q(country=filters["country"])

    if search:
        filter_conditions &= (
            Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(username__icontains=search)
            | Q(display_name__icontains=search)
        )

    return filter_conditions


def build_albums_filter_conditions(
    search: Optional[str],
    filters: dict,
    user: Optional[User] = None,
) -> Q:
    """Albums filter conditions"""
    filter_conditions = Q(deleted=False)

    if user:
        filter_conditions &= Q(user=user)

    else:
        filter_conditions &= Q(is_public=True)

    if "name" in filters:
        filter_conditions &= Q(name__icontains=filters["name"])

    if "description" in filters:
        filter_conditions &= Q(description__icontains=filters["description"])

    if "is_public" in filters:
        filter_conditions &= Q(is_public=filters["is_public"])

    if search:
        filter_conditions &= Q(name__icontains=search) | Q(
            description__icontains=search
        )

    return filter_conditions



def get_product_ids_with_hashtags(hashtags: List[str]) -> List[int]:
    """
    Retrieves product IDs where all specified hashtags exist (case-insensitive).

    Args:
        hashtags (list of str): List of hashtags to filter products by.

    Returns:
        list: IDs of products that partially match all specified hashtags.
    """
    filters = Q()

    for hashtag in hashtags:
        filters |= Q(hashtags__icontains=hashtag)

    products_id = Product.objects.filter(filters).values_list("id", flat=True)

    return products_id


def build_order_filter_conditions(user: User, filters: dict) -> Q:
    """Order filter conditions"""
    filter_conditions = Q()
    is_seller = filters.get("is_seller", False)
    status = filters.get("status") if "status" in filters else None

    if is_seller:
        filter_conditions &= Q(items__product__seller=user)
    else:
        filter_conditions &= Q(user=user)

    if status == ClientOrderStatusEnum.IN_PROGRESS:
        filter_conditions &= Q(
            status__in=[
                OrderStatusEnum.PENDING.value,
                OrderStatusEnum.CONFIRMED.value,
                OrderStatusEnum.SHIPPED.value,
            ]
        )
    elif status == ClientOrderStatusEnum.COMPLETED:
        filter_conditions &= Q(status=OrderStatusEnum.DELIVERED.value)
    elif status == ClientOrderStatusEnum.CANCELLED:
        filter_conditions &= Q(
            status__in=[OrderStatusEnum.CANCELLED.value, OrderStatusEnum.RETURNED.value]
        )

    return filter_conditions


def get_exclusion_queries(user_field: str = "user"):
    """
    Returns exclusion conditions for a specified user-related field.

    Args:
        user_field (str): The name of the user-related field to apply the conditions to
                          (e.g., 'user', 'owner', 'reviewer', 'post_owner').

    Returns:
        Q: A Q object representing the combined exclusion conditions.
    """
    return (
        Q(**{f"{user_field}__is_active": False})
        | Q(**{f"{user_field}__deleted": True})
        | Q(**{f"{user_field}__is_banned": True})
    )


# def get_blocked_user_ids(user: User) -> List[int]:
#     """Retrieve a list of user IDs that the given user has blocked or has been blocked by"""

#     blocked_relations = BlockedUser.objects.filter(Q(user=user) | Q(blocked_users=user))

#     blocked_user_ids = blocked_relations.filter(user=user).values_list(
#         "blocked_users__id", flat=True
#     )
#     blocked_by_user_ids = blocked_relations.filter(blocked_users=user).values_list(
#         "user__id", flat=True
#     )

#     all_blocked_user_ids = list(chain(blocked_user_ids, blocked_by_user_ids))

#     return all_blocked_user_ids


def format_datetime(dt, format_type="default"):
    """
    Format datetime object or ISO string to desired format

    Args:
        dt: datetime object or ISO format string
        format_type: type of format to return ('default', 'short', 'full', 'date_only')

    Returns:
        Formatted datetime string or None if input is None
    """
    if not dt:
        return None

    # Convert string to datetime
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        except ValueError:
            return None

    # Format patterns
    formats = {
        "default": "%B %d, %Y at %I:%M %p",  # October 11, 2024 at 05:10 PM
        "short": "%d %b %Y, %H:%M",  # 11 Oct 2024, 17:10
        "full": "%A, %B %d, %Y at %I:%M %p",  # Thursday, October 11, 2024 at 05:10 PM
        "date_only": "%B %d, %Y",  # October 11, 2024
    }

    try:
        # Convert to local timezone
        local_dt = dt.astimezone(pytz.UTC)
        return local_dt.strftime(formats.get(format_type, formats["default"]))
    except Exception:
        return None


def transform_number(number):
    # Multiply by a large prime number and add a random offset
    multiplier = 982451653  # Large prime number
    random_offset = random.randint(10000000, 99999999)
    transformed_number = number * multiplier + random_offset
    return transformed_number


def reverse_transform(transformed_number):
    multiplier = 982451653  # Large prime number
    offset = random.randint(10000000, 99999999)
    # Subtract the offset first and then divide by the multiplier
    original_number = (transformed_number - offset) // multiplier
    return original_number


def serialize_hashtags_to_camelcase(description=None):
    """
    Extract hashtags from the description and convert them to camelCase.
    """
    import re

    description = "Check out this #cool_product_nike and #awesome_deal! #must_have"
    # Extract hashtags using regex
    hashtags = re.findall(r"#\w+", description)

    # Convert each hashtag to camelCase
    camelcase_hashtags = []
    for hashtag in hashtags:
        # Remove the '#' symbol
        words = hashtag[1:].split("_")
        camelcase = (
            "#"
            + words[0].capitalize()
            + "".join(word.capitalize() for word in words[1:])
        )
        camelcase_hashtags.append(camelcase)

    return camelcase_hashtags


# def broadcast_event_status(event: dict):
#     channel_layer = get_channel_layer()
#     conversation_id = event.pop("conversation_id")
#     event_type = event.pop("type")

#     async_to_sync(channel_layer.group_send)(
#         f"chat_{conversation_id}",
#         {
#             "type": event_type,
#             **event,
#         },
#     )


def calculate_percent_change(new_value, old_value):
    """Calculates the percentage change from old_value to new_value"""

    if old_value > 0:
        percent_change = ((new_value - old_value) / old_value) * 100
    elif old_value == 0 and new_value > 0:
        percent_change = 100
    else:
        percent_change = 0

    return round(percent_change, 2)


def get_cold_start_brands(user_id: int) -> Dict[str, Optional[List[int]]]:
    """
    Fetches popular brands for new users (cold start) as fallback logic.
    This function should be used when `user_likes < 2`.

    Args:
        user_id (int): The ID of the user for whom to fetch popular brands.

    Returns:
        Dict[str, Optional[List[int]]]: A dictionary containing the user_id and a list of brand_ids.
        Returns an empty list of brand_ids if an error occurs.

    Raises:
        ValidationError: If user_id is not a positive integer.
    """
    # Input validation
    if not isinstance(user_id, int) or user_id <= 0:
        raise ValidationError("user_id must be a positive integer")

    try:
        # Construct the query, filter out NULL brand_ids, and execute asynchronously
        query = (
            Product.objects.filter(status=StatusChoices.ACTIVE, brand_id__isnull=False)
            .order_by("-likes")
            .values("brand_id")
            .distinct()[:20]
        )
        # Materialize the QuerySet asynchronously
        rows = query
        brand_ids = [row["brand_id"] for row in rows]
        return {"user_id": user_id, "brand_ids": brand_ids}
    except Exception:
        return {"user_id": user_id, "brand_ids": []}


def generate_short_uuid():
    return str(uuid.uuid4().int)[:10]
