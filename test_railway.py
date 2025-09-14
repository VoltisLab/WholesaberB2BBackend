#!/usr/bin/env python3
"""
Simple test server for Railway deployment.
"""

import os
from django.core.wsgi import get_wsgi_application

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings_railway')

# Get WSGI application
application = get_wsgi_application()

if __name__ == '__main__':
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])
