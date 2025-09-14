#!/bin/bash

# Run database migrations
python manage.py migrate --settings=src.settings_simple_production

# Collect static files
python manage.py collectstatic --noinput --settings=src.settings_simple_production

# Start the application
daphne -b 0.0.0.0 -p $PORT --settings=src.settings_simple_production src.asgi:application
