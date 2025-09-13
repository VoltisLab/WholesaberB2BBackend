from accounts.models import User
from notifications.schema.mutations.notification_mutations import CreateNotification
from products.choices import OrderStatusChoices
from products.models import Order, RecentlyViewedProduct
from utils.jobs.base import BaseTaskWithRetry, only_one
from django.utils import timezone
from celery import shared_task
from django.db import transaction
from utils.non_modular_utils.errors import ErrorException, GenericError
from django.core.management import call_command
from celery.utils.log import get_task_logger
from utils.birthday_messages import generate_birthday_message
from utils.product_utils.shipment_service import ShippingService

logger = get_task_logger(__name__)


@shared_task(bind=True, base=BaseTaskWithRetry, name="send_birthday_notifications")
@only_one
def send_birthday_notifications(self):
    logger.info("picked birthday notification job")

    for user in User.objects.all().exclude(deleted=True).exclude(is_banned=True):
        if (
            user.dob
            and user.dob.day == timezone.now().day
            and user.dob.month == timezone.now().month
        ):
            message = generate_birthday_message(user.username)
            CreateNotification.create_notification(
                user_id=user.id,
                sender=user.id,
                message=message,
                model="USER",
                model_id=user.username,
                model_group="UserBirthday",
                title=user.username,
                info={"page": "USER", "object_id": user.username},
            )


@shared_task(bind=True, base=BaseTaskWithRetry, name="backup_database")
@only_one
def backup_database(self):
    """
    Celery task to backup database
    """
    call_command("backup_db")


@shared_task(bind=True, base=BaseTaskWithRetry, name="update_elasticsearch_index")
@only_one
def update_elasticsearch_index(self):
    """
    Celery task to update elasticsearch index
    """
    call_command("update_elasticsearch_index")


@shared_task(bind=True, base=BaseTaskWithRetry, name="run_product_upload_checks")
@only_one
def run_product_upload_checks(product_id):
    """
    Celery task to run product-upload checks.
    """
    from utils.product_utils.product_utils import ProductUploadChecker

    checker = ProductUploadChecker(product_id)
    checker.perform_checks()


@shared_task(
    bind=True, base=BaseTaskWithRetry, name="update_recently_viewed"
)  # TODO: Use RabbitMQ
@only_one
def update_recently_viewed(self, user_id, product_id):
    """
    Updates or creates a recently viewed product record for a user,
    and enforces the maximum limit of recently viewed products.
    Uses bulk operations for better performance.

    Args:
        user_id (int): The ID of the user who viewed the product.
        product_id (int): The ID of the product that was viewed.

    Returns:
        None
    """
    MAX_RECENTLY_VIEWED = 20

    try:
        with transaction.atomic():
            # Update or create the recently viewed product record
            viewed_at = timezone.now()
            RecentlyViewedProduct.objects.update_or_create(
                user_id=user_id,
                product_id=product_id,
                defaults={"viewed_at": viewed_at},
            )

            # Get all recently viewed products for this user, ordered by viewed_at
            user_viewed_products = RecentlyViewedProduct.objects.filter(
                user_id=user_id
            ).order_by("-viewed_at")

            # If we have more than the maximum, delete all excess records in one query
            if user_viewed_products.count() > MAX_RECENTLY_VIEWED:
                products_to_keep = user_viewed_products[:MAX_RECENTLY_VIEWED]
                RecentlyViewedProduct.objects.filter(user_id=user_id).exclude(
                    id__in=[p.id for p in products_to_keep]
                ).delete()

    except Exception as e:
        raise ErrorException(
            message=f"An error occurred while updating the recently viewed products. {e}",
            error_type=GenericError,
            meta={},
            code=422,
        )


@shared_task(bind=True, base=BaseTaskWithRetry, name="update_shipment")
@only_one
def update_shipment(self):
    """
    Celery task to update shipment status
    """
    orders = Order.objects.filter(status=OrderStatusChoices.CONFIRMED)
    ShippingService.process_order_shipment(orders, OrderStatusChoices.SHIPPED)


@shared_task(bind=True, base=BaseTaskWithRetry, name="order_in_transit")
@only_one
def order_in_transit(self):
    """
    Celery task to update shipment status
    """
    orders = Order.objects.filter(status=OrderStatusChoices.SHIPPED)
    ShippingService.process_order_shipment(orders, OrderStatusChoices.IN_TRANSIT)


@shared_task(bind=True, base=BaseTaskWithRetry, name="order_ready_for_pickup")
@only_one
def order_ready_for_pickup(self):
    """
    Celery task to update shipment status
    """
    orders = Order.objects.filter(status=OrderStatusChoices.IN_TRANSIT)
    ShippingService.process_order_shipment(orders, OrderStatusChoices.READY_FOR_PICKUP)


@shared_task(bind=True, base=BaseTaskWithRetry, name="order_delivered")
@only_one
def order_delivered(self):
    """
    Celery task to update shipment status
    """
    orders = Order.objects.filter(status=OrderStatusChoices.READY_FOR_PICKUP)
    ShippingService.process_order_shipment(orders, OrderStatusChoices.DELIVERED)
