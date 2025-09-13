from decimal import Decimal
from django.db import models
from accounts.models import User

from products.choices import (
    Condition,
    ParcelSizeChoices,
    SizeSubTypeChoices,
    SizeTypeChoices,
    StatusChoices,
    StyleChoices,
)

NULL = {"null": True, "blank": True}


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, **NULL, related_name="children"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_full_path(self):
        """Returns the full path of category from root to this node"""
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name


class Size(models.Model):
    name = models.CharField(max_length=50)
    size_type = models.CharField(max_length=20, choices=SizeTypeChoices.choices, **NULL)
    size_subtype = models.CharField(
        max_length=20, choices=SizeSubTypeChoices.choices, **NULL
    )

    def __str__(self):
        return f"{self.name} ({self.size_type})"


class Product(models.Model):
    name = models.CharField(max_length=200)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products")
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, **NULL)
    size = models.ForeignKey(Size, on_delete=models.CASCADE, **NULL)
    style = models.CharField(max_length=50, choices=StyleChoices.choices, **NULL)
    parcel_size = models.CharField(
        max_length=50, choices=ParcelSizeChoices.choices, **NULL
    )
    condition = models.CharField(max_length=50, choices=Condition.choices, **NULL)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    images_url = models.JSONField(default=list)
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
    )
    materials = models.ManyToManyField(
        "Material", related_name="material_products", blank=True
    )
    color = models.JSONField(default=list, **NULL)
    brand = models.ForeignKey("Brand", on_delete=models.SET_NULL, **NULL)
    custom_brand = models.CharField(max_length=100, **NULL)
    hashtags = models.JSONField(default=list, blank=True)
    is_featured = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Material(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ProductLike(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class ProductView(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    viewed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Banner(models.Model):
    title = models.CharField(max_length=100)
    style = models.CharField(
        max_length=50,
        choices=StyleChoices.choices,
        default=StyleChoices.PARTY_OUTFIT,
        unique=True,
    )
    banner_url = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, **NULL)
    updated_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="updated_by", **NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, **NULL)

    def __str__(self):
        return f"{self.title} - {self.style}"


class RecentlyViewedProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-viewed_at"]
        unique_together = ["user", "product"]
