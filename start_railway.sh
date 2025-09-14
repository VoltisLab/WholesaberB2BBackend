#!/bin/bash

# Exit on any error
set -e

echo "Starting Railway deployment..."

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --settings=src.settings_railway

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --settings=src.settings_railway

# Start the application
echo "Starting Django application..."
python manage.py runserver 0.0.0.0:$PORT --settings=src.settings_railway
