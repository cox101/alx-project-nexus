#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Navigate to project directory
cd ChaguaSmart

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate