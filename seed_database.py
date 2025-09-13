#!/usr/bin/env python
"""
Script to seed the database with fake data for testing
Run this from the project root directory
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

if __name__ == "__main__":
    # Setup Django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.settings")
    django.setup()
    
    # Run the seed command
    execute_from_command_line([
        'manage.py', 
        'seed_data',
        '--users', '100',
        '--vendors', '30', 
        '--products', '500',
        '--orders', '200'
    ])

