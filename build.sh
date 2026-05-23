#!/usr/bin/env bash
set -o errexit

echo "Python version: $(python --version)"

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Running migrations..."
python manage.py migrate

echo "Creating superuser if not exists..."
python manage.py shell << 'PYEOF'
import os
from django.contrib.auth import get_user_model
User = get_user_model()

email    = os.environ.get('DJANGO_SUPERUSER_EMAIL',    'admin@jobportal.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'Admin@123456')
fname    = os.environ.get('DJANGO_SUPERUSER_FIRSTNAME', 'Super')
lname    = os.environ.get('DJANGO_SUPERUSER_LASTNAME',  'Admin')

if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(
        email=email,
        password=password,
        first_name=fname,
        last_name=lname,
    )
    print(f'Superuser created: {email}')
else:
    print(f'Superuser already exists: {email}')
PYEOF

echo "Build complete!"