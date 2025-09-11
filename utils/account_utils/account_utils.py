from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from accounts.choices import GenderChoice
from accounts.models import (
    User,

)
from accounts.schema.accounts_responses import (
    BIRTHDAY_COUNT_EXCEEDED,
    BLOCKED_USER_SUCCESS,
    FOLLOW_DOES_NOT_EXIST,
    FOLLOW_EXISTS,
    FOLLOW_SELF,
    OBJECT_EXISTS,
    REVIEWS,
    UNBLOCKED_USER_SUCCESS,
    USER_BLOCKED_DOES_NOT_EXIST,
    USER_BLOCKED_SELF,
    USER_DOES_NOT_EXIST,
    INVALID_USER_TYPE,
)
from django.core.cache import cache
from django.db import transaction
from notifications.schema.mutations.notification_mutations import CreateNotification
from products.models import ProductLike
from products.schema.product_responses import ORDER_DOES_NOT_EXIST
from utils.non_modular_utils.errors import ErrorException, GenericError, StandardError
from utils.security.otp_service import OTPManager
from utils.upload_utils import UploadUtil
from utils.utils import (
    get_template_path,
)

from accounts.schema.enums.accounts_enums import GenderEnum

class AccountsUtil:
    @staticmethod
    def update_user(user, **kwargs):
        """
        Update the user's attributes with the given keyword arguments.

        This method updates various attributes of the user, such as personal information,
        profile details, and settings. It ensures that the username is unique before updating it.

        Parameters:
        user (User): The user object to be updated.
        **kwargs (dict): A dictionary of attributes to be updated. The keys should be among the following:
            - first_name
            - last_name
            - username
            - bio
            - profile_picture
            - gender
            - phone_number (dict): A dictionary with keys 'countryCode', 'number', and 'completed'.
            - country
            - postcode
            - display_name
            - dob
            - location (dict): A dictionary with keys 'latitude' and 'longitude'.
            - use_2fa
            - preferred_currency
            - shipping_address (dict): A dictionary with keys 'address', 'city', 'state', 'country', and 'postcode'.
            - user_type

        Raises:
        ErrorException: If the user type is invalid.
        ValueError: If the username already exists or if the DOB change count exceeds the limit.

        """
        otp = kwargs.pop("otp", None)

        # Update basic attributes
        basic_updates = [
            "first_name",
            "last_name",
            "bio",
            "country",
            "postal_code",
            "display_name",
            "is_vacation_mode",
            "street_address",
            "city",
            "postal_code"
            "preferred_currency",
            "shipping_address",
            "user_type",
        ]
        # Iterate over the provided kwargs and update corresponding attributes
        for attr in basic_updates:
            if attr in kwargs and kwargs[attr] is not None:
                value = kwargs[attr]
                setattr(user, attr, value)

        if "gender" in kwargs:
            AccountsUtil._update_gender(user, kwargs.get("gender"))

        if "dob" in kwargs:
            AccountsUtil._update_dob(user, kwargs.get("dob"))

        if "profile_picture" in kwargs:
            AccountsUtil._update_profile_picture(user, kwargs.get("profile_picture"))

        if "phone_number" in kwargs:
            AccountsUtil._update_phone_number(user, kwargs.get("phone_number"))
        
        if "account_type" in kwargs:
            user.account_type = kwargs.get("account_type").value
        
        if "email_address" in kwargs :
            if User.objects.filter(email=kwargs.get("email_address")).exclude(id=user.id).exists():
                raise ValueError("Email address already exists.")
            user.email = kwargs.get("email_address")
        user.save()
        return user

    @staticmethod
    def _update_username(user, username):
        # Check if 30 days have passed since the last username update
        if user.username_last_updated:
            thirty_days_ago = timezone.now() - timedelta(days=30)
            if user.username_last_updated > thirty_days_ago:
                days_left = 30 - (timezone.now() - user.username_last_updated).days
                raise ValueError(
                    f"Username can only be updated once every 30 days. Please try again in {days_left} days."
                )

        # Check if the new username already exists
        if User.objects.filter(username=username).exists():
            raise ValueError(f"Username '{username}' is already taken.")

        # Update username and timestamp
        user.username_last_updated = timezone.now()
        user.username = username

    @staticmethod
    def _update_gender(user, gender):
        mapping = {
            GenderEnum.MALE: GenderChoice.MALE,
            GenderEnum.FEMALE: GenderChoice.FEMALE,
            GenderEnum.OTHER: GenderChoice.OTHER,
            GenderEnum.PREFER_NOT_TO_SAY: GenderChoice.PREFER_NOT_TO_SAY,
        }
        user.gender = mapping.get(gender)
        user.save()

    @staticmethod
    def _update_dob(user, dob):
        if dob and dob != user.dob:
            if user.dob_change_count >= 3:
                raise ValueError(BIRTHDAY_COUNT_EXCEEDED)
            user.dob = dob
            user.dob_change_count += 1
    
    def _update_profile_picture(user, profile_picture):
        if "profile_picture_url" in profile_picture:
            user.profile_picture_url = profile_picture["profile_picture_url"]
        
        if "thumbnail_url" in profile_picture:
            user.thumbnail_url = profile_picture["thumbnail_url"]
    
    def _update_phone_number(user, phone_number):
        user.phone_number = phone_number


    @staticmethod
    def add_delivery_address(user, **kwargs):
        from accounts.models import DeliveryAddress
        address_type = kwargs.get("address_type").value
        kwargs["address_type"] = address_type
        address = DeliveryAddress.objects.create(user=user, **kwargs)

        if address.is_default:
            DeliveryAddress.objects.filter(user=user, is_default=True).exclude(id=address.id).update(is_default=False)
        return address

    @staticmethod
    def update_delivery_address(user, address_id, **kwargs):
        from accounts.models import DeliveryAddress
        try:
            address = DeliveryAddress.objects.get(id=address_id, user=user)
        except DeliveryAddress.DoesNotExist:
            raise ValueError("Delivery address does not exist.")
        
        if "address_type" in kwargs:
            kwargs["address_type"] = kwargs.get("address_type").value
        
        if "is_default" in kwargs and kwargs.get("is_default"):
            DeliveryAddress.objects.filter(user=user, is_default=True).exclude(id=address.id).update(is_default=False)
        
        for attr, value in kwargs.items():
            if value is not None:
                setattr(address, attr, value)
        
        address.save()

        if address.is_default:
            DeliveryAddress.objects.filter(user=user, is_default=True).exclude(id=address.id).update(is_default=False)
        
        return address
    
    @staticmethod
    def delete_delivery_address(user, address_id):
        from accounts.models import DeliveryAddress
        try:
            address = DeliveryAddress.objects.get(id=address_id, user=user)
            address.delete()
            return True
        except DeliveryAddress.DoesNotExist:
            raise ValueError("Delivery address does not exist.")