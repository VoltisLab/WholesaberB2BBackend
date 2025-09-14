#!/bin/bash

# Run database migrations
python manage.py migrate --settings=src.settings_railway

# Collect static files
python manage.py collectstatic --noinput --settings=src.settings_railway

# Start the application
daphne -b 0.0.0.0 -p $PORT --settings=src.settings_railway src.asgi:application
