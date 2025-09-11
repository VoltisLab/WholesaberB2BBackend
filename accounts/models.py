from django.db import models

from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)

NULL = {"blank": True, "null": True}

from phonenumber_field.modelfields import PhoneNumberField
from accounts.choices import GenderChoice, AccountType
from django.utils import timezone


class UserManager(BaseUserManager):
    def create(self, username, **kwargs):
        # if username is None:
        #     raise ValueError("username can not be null")

        user = self.model(username=username, **kwargs)
        user.set_password(kwargs.get("password"))
        user.save(using=self._db)
        return user

    def create_superuser(self, username, **kwargs):
        kwargs["is_staff"] = True
        kwargs["is_superuser"] = True
        return self.create(username=username, **kwargs)

    def create_user(self, username, **kwargs):
        return self.create(username=username, **kwargs)


# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(
        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, **NULL)
    username = models.CharField(max_length=100, unique=True, **NULL)
    dob = models.DateField(**NULL)
    dob_change_count = models.IntegerField(default=0)
    email = models.EmailField(unique=True, **NULL)
    profile_picture_url = models.CharField(max_length=255, **NULL)
    thumbnail_url = models.URLField(blank=True, null=True)
    gender = models.CharField(max_length=25, choices=GenderChoice.choices, **NULL)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    display_name = models.CharField(max_length=100, **NULL)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    phone_number = PhoneNumberField(unique=True, **NULL)
    date_joined = models.DateTimeField(default=timezone.localtime, editable=False)
    account_type = models.CharField(
        max_length=25,
        choices=AccountType.choices,
        default=AccountType.CUSTOMER,
    )
    city = models.CharField(max_length=100, **NULL)
    street_address = models.CharField(max_length=255, **NULL)
    postal_code = models.CharField(max_length=20, **NULL)
    last_login = models.DateTimeField(**NULL)
    last_seen = models.DateTimeField(**NULL)
    meta = models.JSONField(default=dict, **NULL)
    terms_accepted = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    objects = UserManager()
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class PhoneVerification(models.Model):
    """Model for phone verification OTP"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="phone_verifications"
    )
    phone_number = models.CharField(max_length=20)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    attempts = models.PositiveIntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=["user", "is_used"]),
            models.Index(fields=["phone_number", "otp_code"]),
        ]

    def is_expired(self):
        return timezone.now() > self.expires_at

    def increment_attempts(self):
        self.attempts += 1
        self.save(update_fields=["attempts"])

    def __str__(self):
        return f"Phone verification for {self.user.email}"


class Verification(models.Model):
    user = models.OneToOneField(
        User, related_name="otp", unique=True, on_delete=models.CASCADE
    )
    code = models.CharField(max_length=10, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email


class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    # result_count = models.IntegerField(null=True, blank=True)
    search_type = models.CharField(max_length=100, null=True, blank=True)
    deleted = models.BooleanField(default=False)
    search_count = models.IntegerField(default=1)
    search_frequency = models.IntegerField(default=1)
    last_searched = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-timestamp"]


class DeliveryAddress(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="delivery_addresses"
    )
    address_type = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    phone_number = PhoneNumberField()
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100, **NULL)
    is_default = models.BooleanField(default=False)
    postal_code = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.address_type}"
