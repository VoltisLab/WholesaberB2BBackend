#!/usr/bin/env python3
"""
Minimal Django app for AWS Elastic Beanstalk testing.
"""

import os
import sys
import django
from django.conf import settings
from django.core.wsgi import get_wsgi_application
from django.http import JsonResponse
from django.urls import path
from django.conf.urls import url

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Minimal Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings_simple_production')

# Initialize Django
django.setup()

def health_check(request):
    return JsonResponse({
        'status': 'success',
        'message': 'AWS Elastic Beanstalk Django backend is working!',
        'method': request.method,
        'path': request.path
    })

# Minimal URL configuration
urlpatterns = [
    path('', health_check),
    path('test/', health_check),
    path('health/', health_check),
]

# Get WSGI application
application = get_wsgi_application()

if __name__ == '__main__':
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])
