#!/bin/sh

# Function to wait for Redis (optional, but good practice)
if [ "$CELERY_BROKER_URL" ]; then
    echo "Waiting for Redis..."
    while ! nc -z redis 6379; do
      sleep 0.1
    done
    echo "Redis started"
fi

if [ "$1" = 'web' ]; then
    echo "Running migrations..."
    python manage.py migrate --noinput
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
    echo "Starting Gunicorn..."
    exec gunicorn url_shortener.wsgi:application --bind 0.0.0.0:8000
elif [ "$1" = 'dev' ]; then
    echo "Running migrations..."
    python manage.py migrate --noinput
    echo "Starting Development Server (Hot Reloading)..."
    exec python manage.py runserver 0.0.0.0:8000
elif [ "$1" = 'worker' ]; then
    echo "Starting Celery worker..."
    exec celery -A url_shortener worker --loglevel=info
else
    exec "$@"
fi
