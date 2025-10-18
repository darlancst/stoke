#!/usr/bin/env bash
# Build script for Render.com deployment

set -o errexit  # Exit on error

echo "==> Installing Python dependencies..."
pip install -r requirements.txt

echo "==> Navigating to Django project directory..."
cd estoque_project

echo "==> Collecting static files..."
python manage.py collectstatic --no-input

echo "==> Running database migrations..."
python manage.py migrate --no-input

echo "==> Resetting and recreating superuser from environment variables..."
echo "Username: $DJANGO_SUPERUSER_USERNAME"
echo "Email: $DJANGO_SUPERUSER_EMAIL"
echo "Password configured: $(if [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then echo "YES"; else echo "NO"; fi)"
python manage.py reset_superuser || echo "⚠️ WARNING: Failed to reset superuser"

echo "==> Returning to root directory..."
cd ..

echo "==> Build completed successfully!"

