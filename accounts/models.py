from django.db import models

from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)

NULL = {"blank": True, "null": True}

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
    date_joined = models.DateTimeField(default=timezone.localtime, editable=False)
    account_type = models.CharField(
        max_length=25,
        choices=AccountType.choices,
        default=AccountType.customer,
    )
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
