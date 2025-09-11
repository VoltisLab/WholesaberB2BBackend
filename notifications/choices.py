from django.db import models


class NotificationChoices(models.TextChoices):
    LIKES = "likes", "Likes"
    NEW_FOLLOWERS = "new_followers", "New Followers"
    PROFILE_VIEW = "profile_view", "Profile View"
    PRODUCT_VIEW = "product_view", "Product View"
    MESSAGES = "messages", "Messages"
