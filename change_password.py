#!/usr/bin/env python3
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
django.setup()

from django.contrib.auth import get_user_model

# Get user and change password
User = get_user_model()
user = User.objects.get(email='toziz@yahoo.com')
user.set_password('Password123!!!')
user.save()

print(f'✅ Password updated for {user.email}')
print(f'✅ Password verification: {user.check_password("Password123!!!")}')
