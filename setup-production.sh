#!/bin/bash

# HomeChefs AI Production Setup Script
# This script helps set up the production environment

echo "🚀 Setting up HomeChefs AI Production Environment"
echo "================================================"

# Check if .env exists
if [ -f ".env" ]; then
    echo "✅ .env file already exists"
    echo "⚠️  Please update it manually with your production values"
    echo "📋 Current .env file:"
    cat .env
else
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created from template"
    echo "⚠️  IMPORTANT: Update .env with your production values!"
fi

echo ""
echo "🔧 Next Steps:"
echo "1. Edit .env file with your production settings:"
echo "   - SECRET_KEY: Generate a new secure key"
echo "   - DATABASE_URL: PostgreSQL connection string"
echo "   - REDIS_URL: Redis connection string"
echo "   - EMAIL_*: Your email configuration"
echo "   - ALLOWED_HOSTS: Your domain names"
echo ""
echo "2. Install production dependencies:"
echo "   pip install -r requirements-prod.txt"
echo ""
echo "3. Set up PostgreSQL database:"
echo "   - Create database and user"
echo "   - Update DATABASE_URL in .env"
echo ""
echo "4. Set up Redis server:"
echo "   - Install Redis on port 6379"
echo "   - Update REDIS_URL in .env"
echo ""
echo "5. Configure domain and SSL:"
echo "   - Point domain to your server"
echo "   - Set up SSL certificate"
echo "   - Update ALLOWED_HOSTS in .env"
echo ""
echo "6. Generate Django secret key:"
echo "   python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'"
echo "   - Update SECRET_KEY in .env"
echo ""
echo "🎯 Production Commands:"
echo "   Collect static files: python manage.py collectstatic --noinput"
echo "   Run migrations:     python manage.py migrate"
echo "   Start server:      gunicorn HomeChefs.wsgi:application --bind 0.0.0.0:8000"
echo ""
echo "📚 For detailed setup guide, see: README.md"
