#!/usr/bin/env bash

set -o errexit  # Exit on error

# Upgrade pip to the latest version
pip install --upgrade pip

# Set DJANGO_SETTINGS_MODULE to settings.production
export DJANGO_SETTINGS_MODULE=settings.prod

# Install the required packages
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate

# Create superuser
python manage.py createsu