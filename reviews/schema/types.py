import graphene
from graphene_django import DjangoObjectType
from reviews.models import Review, ReviewHelpful, ReviewResponse, ProductRating, VendorRating


class ReviewType(DjangoObjectType):
    class Meta:
        model = Review
        fields = "__all__"


class ReviewHelpfulType(DjangoObjectType):
    class Meta:
        model = ReviewHelpful
        fields = "__all__"


class ReviewResponseType(DjangoObjectType):
    class Meta:
        model = ReviewResponse
        fields = "__all__"


class ProductRatingType(DjangoObjectType):
    class Meta:
        model = ProductRating
        fields = "__all__"


class VendorRatingType(DjangoObjectType):
    class Meta:
        model = VendorRating
        fields = "__all__"
