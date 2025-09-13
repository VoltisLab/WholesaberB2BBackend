from django.db import models
from accounts.models import User

# Create your models here.

class SMS2FA(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
