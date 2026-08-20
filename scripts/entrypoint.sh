#!/bin/bash
set -e

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "✅ Database is ready!"

# Wait for Redis to be ready
echo "⏳ Waiting for Redis to be ready..."
while ! nc -z $REDIS_HOST $REDIS_PORT; do
  sleep 0.1
done
echo "✅ Redis is ready!"

# Run database migrations
echo "🗃️ Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist
echo "👤 Creating superuser..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@homechefhub.in', 'admin123')
    print('Superuser created successfully')
else:
    print('Superuser already exists')
EOF

# Start the application
echo "🚀 Starting the application..."
exec "$@"
