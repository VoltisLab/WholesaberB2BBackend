import jinja2
from django.conf import settings
from products.choices import OrderStatusChoices, ShippingServiceProvider
from products.models import Shipment
from utils.utils import (
    broadcast_event_status,
    format_datetime,
    get_template_path,
    transform_number,
)
from django.core.mail import send_mail


class ShippingService:
    def __init__(self, order):
        self.order = order
        self.order_id = transform_number(order.id)
        self.raw_order_id = order.id

    def create_shipment(self, pickup_address, shipping_service):
        """Create a shipment for the order with addresses"""
        shipment = Shipment.objects.create(
            order=self.order,
            pickup_address=pickup_address,
            shipping_service=shipping_service,
        )
        # self._notify_seller()
        return shipment

    def update_shipment(self, status, tracking_number=None, tracking_url=None):
        VALID_TRANSITIONS = {
            OrderStatusChoices.PENDING: [
                OrderStatusChoices.CONFIRMED,
                OrderStatusChoices.SHIPPED,  # For testing purposes
                OrderStatusChoices.CANCELLED,
            ],
            OrderStatusChoices.CONFIRMED: [
                OrderStatusChoices.SHIPPED,
                OrderStatusChoices.CANCELLED,
            ],
            OrderStatusChoices.SHIPPED: [
                OrderStatusChoices.IN_TRANSIT,
                OrderStatusChoices.DELIVERED,
                OrderStatusChoices.CANCELLED,
            ],
            OrderStatusChoices.IN_TRANSIT: [
                OrderStatusChoices.READY_FOR_PICKUP,
                OrderStatusChoices.DELIVERED,
                OrderStatusChoices.CANCELLED,
            ],
            OrderStatusChoices.READY_FOR_PICKUP: [
                OrderStatusChoices.DELIVERED,
                OrderStatusChoices.RETURNED,
                OrderStatusChoices.CANCELLED,
            ],
            OrderStatusChoices.DELIVERED: [
                OrderStatusChoices.COMPLETED,
                OrderStatusChoices.RETURNED,
            ],
            OrderStatusChoices.CANCELLED: [],
            OrderStatusChoices.RETURNED: [],
        }
        try:
            shipment = self.order.shipment
        except Shipment.DoesNotExist:
            # raise ValueError("No shipment exists for this order")
            return

        # Validate status transition
        if status not in VALID_TRANSITIONS.get(shipment.status, []):
            raise ValueError(
                f"Invalid status transition from {shipment.status} to {status}"
            )

        # Update shipment
        shipment.status = status
        if tracking_number:
            shipment.tracking_number = tracking_number
        if tracking_url:
            shipment.tracking_url = tracking_url

        shipment.save()

        # Update order status
        self.order.status = status
        self.order.save()

        # if status not in [
        #     OrderStatusChoices.IN_TRANSIT,
        #     OrderStatusChoices.READY_FOR_PICKUP,
        # ]:

        # Update order related conversation' last modified, if conversation exist
        related_conversation = self.order.conversation.all()
        related_conversation.update(last_modified=self.order.updated_at)

        # Broadcast the status update
        if related_conversation.exists():
            conversation = related_conversation.first()
            event = {
                "type": "order_status_event",
                "order_id": self.raw_order_id,
                "status": status,
                "conversation_id": conversation.id,
            }
            broadcast_event_status(event)

        # Notify relevant parties about the status change
        self._notify_status_update(status)

    def generate_shipping_label(self):
        """Generate shipping label based on shipping service and addresses"""
        shipment = self.order.shipment
        if not shipment:
            raise ValueError("No shipment exists for this order")

        label_generators = {
            ShippingServiceProvider.DPD: self._generate_dhl_label,
            ShippingServiceProvider.EVRI: self._generate_evri_label,
            ShippingServiceProvider.UDEL: self._generate_udel_label,
            ShippingServiceProvider.ROYAL_MAIL: self._generate_roayl_mail_label,
        }

        # Get the corresponding label generation function
        generate_label = label_generators.get(shipment.shipping_service)

        if generate_label:
            label_url = generate_label(shipment.pickup_address)
            shipment.shipping_label_url = label_url
            shipment.save()
            return label_url
        else:
            raise ValueError(
                f"No valid label generator for {shipment.shipping_service}"
            )

    def _notify_status_update(self, status):
        """Send notifications based on shipment status changes"""
        notifications = {
            OrderStatusChoices.SHIPPED: self._notify_shipment,
            OrderStatusChoices.IN_TRANSIT: self._notify_in_transit,
            OrderStatusChoices.READY_FOR_PICKUP: self._notify_ready_for_pickup,
            OrderStatusChoices.DELIVERED: self._notify_delivery,
            OrderStatusChoices.CANCELLED: self._notify_cancellation,
            OrderStatusChoices.RETURNED: self._notify_return,
        }

        notify_method = notifications.get(status)
        if notify_method:
            notify_method()

    def _notify_shipment(self):
        """Notify buyer about shipment"""
        template = get_template_path("order_shipped")

        context = {
            "buyer_name": self.order.user.get_full_name(),
            "order_id": self.order_id,
            "products": self.order.get_items(),
            "tracking_number": self.order.shipment.tracking_number,
            "tracking_url": self.order.shipment.tracking_url,
            "estimated_delivery": self.order.shipment.estimated_delivery_date,
            "discount_price": self.order.discount_price,
            "shipping_fee": self.order.shipping_fee,
            "price_total": self.order.price_total,
        }
        self._send_notification_email(
            template_path=template,
            context=context,
            subject=f"Your Order #{self.order_id} Has Been Shipped",
            recipient_email=self.order.user.email,
        )

    def _notify_ready_for_pickup(self):
        """Notify buyer that order is ready for pickup"""
        template = get_template_path("order_ready_pickup")
        context = {
            "buyer_name": self.order.user.get_full_name(),
            "order_id": self.order_id,
            "products": self.order.get_items(),
            "shipping_service": self.order.shipment.get_shipping_service_display(),
            "discount_price": self.order.discount_price,
            "shipping_fee": self.order.shipping_fee,
            "price_total": self.order.price_total,
        }
        self._send_notification_email(
            template_path=template,
            context=context,
            subject=f"Order #{self.order_id} Ready for Pickup",
            recipient_email=self.order.user.email,
        )

    def _notify_delivery(self):
        """Notify seller and buyer about delivery"""
        # Notify seller
        seller_template = get_template_path("seller_order_delivered")
        seller_context = {
            "seller_name": self.order.seller.get_full_name(),
            "order_id": self.order_id,
            "products": self.order.get_items(),
            "delivery_date": format_datetime(self.order.shipment.updated_at),
        }
        self._send_notification_email(
            template_path=seller_template,
            context=seller_context,
            subject=f"Order #{self.order_id} Delivered Successfully",
            recipient_email=self.order.seller.email,
        )

        # Notify buyer
        buyer_template = get_template_path("buyer_order_delivered")
        buyer_context = seller_context.copy()
        buyer_context["buyer_name"] = self.order.user.get_full_name()

        self._send_notification_email(
            template_path=buyer_template,
            context=buyer_context,
            subject=f"Order #{self.order_id} Delivered",
            recipient_email=self.order.user.email,
        )

    def _notify_in_transit(self):
        """Notify buyer about in-transit status"""
        pass

    def _notify_cancellation(self):
        """Notify both parties about order cancellation"""
        pass

    def _notify_return(self):
        """Notify seller about return"""
        pass

    def _send_notification_email(
        self, template_path, context, subject, recipient_email
    ):
        """Helper method to send notification emails"""
        try:
            with open(template_path, "r") as file:
                template = file.read()

            html_body = jinja2.Template(template).render(context)

            send_mail(
                subject=subject,
                message="body",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient_email],
                html_message=html_body,
            )
        except Exception as e:
            print(f"Failed to send notification email: {str(e)}")

    def send_shipping_label_to_seller(self):
        """Send the shipping label to the seller"""
        shipment = self.order.shipment
        if not shipment:
            raise ValueError("No shipment exists for this order")

        # Send the shipping label to the seller
        self.send_shipping_label_email()

    def send_shipping_label_email(self):
        """Send shipping label email to seller"""
        template_path = get_template_path("shipping_label")
        context = {
            "seller_name": self.order.seller.get_full_name(),
            "order_id": self.order_id,
            "shipping_service": self.order.shipment.get_shipping_service_display(),
            # "tracking_number": self.order.shipment.tracking_number,
            # "shipping_label_url": self.order.shipment.shipping_label_url,
            "buyer_name": self.order.user.get_full_name(),
        }

        with open(template_path, "r") as file:
            body = file.read()

        html_body = jinja2.Template(body).render(context)

        send_mail(
            subject=f"Shipping Label Ready for Order #{self.order_id}",
            message="body",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.order.seller.email],
            html_message=html_body,
        )

    def _generate_dhl_label(self, pickup_address):
        return "https://shipping-labels.example.com/dhl-label.pdf"

    def _generate_evri_label(self, pickup_address):
        return "https://shipping-labels.example.com/evri-label.pdf"

    def _generate_udel_label(self, pickup_address):
        return "https://shipping-labels.example.com/udel-label.pdf"

    def _generate_roayl_mail_label(self, pickup_address):
        return "https://shipping-labels.example.com/royal-mail-label.pdf"

    @staticmethod
    def process_order_shipment(
        orders, new_status
    ):  # TODO: Remove this method when shipment is fully implemented
        """
        Helper function to process the shipment for given orders and update their status.
        """
        for order in orders:
            try:
                shipment = order.shipment
                if shipment:
                    shipping_service = ShippingService(order)
                    shipping_service.update_shipment(new_status)

                    if new_status == OrderStatusChoices.SHIPPED:
                        shipping_service.send_shipping_label_to_seller()

            except Exception as e:
                print(f"Error processing order {order.id}: {str(e)}")
                continue
