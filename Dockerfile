# Use Python 3.10 slim image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        gettext \
        curl \
        netcat-traditional \
        nginx \
        supervisor \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements-prod.txt /app/
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements-prod.txt

# Copy project
COPY . /app/

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/mediafiles /app/logs /var/log/django

# Copy configuration files
COPY nginx.conf /etc/nginx/sites-available/homechefs
COPY gunicorn.conf.py /app/
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create scripts directory and copy scripts
RUN mkdir -p /app/scripts
COPY scripts/ /app/scripts/

# Make scripts executable
RUN chmod +x /app/scripts/*.sh

# Set permissions
RUN chown -R www-data:www-data /app/staticfiles /app/mediafiles /app/logs

# Create Django superuser script
RUN echo 'from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser("admin", "admin@homechefhub.in", "admin123") if not User.objects.filter(username="admin").exists() else None' > /app/create_superuser.py

# Collect static files
RUN python manage.py collectstatic --noinput --settings=HomeChefs.settings_production || true

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/admin/ || exit 1

# Start supervisor
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
