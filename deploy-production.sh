#!/bin/bash

# HomeChefs AI Production Deployment Script
# Automates the deployment process for production environment

set -e  # Exit on any error

echo "🚀 HomeChefs AI Production Deployment"
echo "====================================="

# Configuration
PROJECT_DIR="/path/to/homechefs_ai"  # UPDATE THIS PATH
VENV_DIR="$PROJECT_DIR/venv"
SERVICE_NAME="homechefs_ai"
NGINX_CONF="/etc/nginx/sites-available/homechefs_ai"
SYSTEMD_SERVICE="/etc/systemd/system/homechefs_ai.service"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    log_error "This script must be run as root"
    exit 1
fi

# Check if .env exists
if [ ! -f "$PROJECT_DIR/.env" ]; then
    log_error ".env file not found. Please create it from .env.example"
    exit 1
fi

log_info "Starting deployment process..."

# 1. Update system packages
log_info "Updating system packages..."
apt update && apt upgrade -y

# 2. Install dependencies
log_info "Installing system dependencies..."
apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx certbot python3-certbot-nginx

# 3. Set up Python virtual environment
if [ ! -d "$VENV_DIR" ]; then
    log_info "Creating Python virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

log_info "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# 4. Install Python dependencies
log_info "Installing Python dependencies..."
pip install -r "$PROJECT_DIR/requirements-prod.txt"

# 5. Set up PostgreSQL
log_info "Setting up PostgreSQL database..."
sudo -u postgres psql -f "$PROJECT_DIR/setup-database.sql"

# 6. Set up Redis
log_info "Setting up Redis..."
systemctl enable redis-server
systemctl start redis-server

# 7. Collect static files
log_info "Collecting static files..."
cd "$PROJECT_DIR"
python manage.py collectstatic --noinput --clear

# 8. Run database migrations
log_info "Running database migrations..."
python manage.py migrate

# 9. Create superuser (interactive)
log_info "Creating Django superuser..."
python manage.py createsuperuser

# 10. Set up Gunicorn systemd service
log_info "Setting up Gunicorn service..."
cat > "$SYSTEMD_SERVICE" << EOF
[Unit]
Description=HomeChefs AI Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/gunicorn --config gunicorn.conf.py
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl start "$SERVICE_NAME"

# 11. Set up Nginx
log_info "Setting up Nginx configuration..."
cp "$PROJECT_DIR/nginx.conf" "$NGINX_CONF"
ln -sf "$NGINX_CONF" "/etc/nginx/sites-enabled/homechefs_ai"
nginx -t
systemctl reload nginx

# 12. Set up SSL certificate
log_info "Setting up SSL certificate..."
certbot --nginx -d yourdomain.com --non-interactive --agree-tos --email admin@yourdomain.com

# 13. Set up firewall
log_info "Configuring firewall..."
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8000/tcp
ufw --force enable

# 14. Set up log rotation
log_info "Setting up log rotation..."
cat > "/etc/logrotate.d/homechefs_ai" << EOF
/var/log/gunicorn/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload homechefs_ai
    endscript
}

/var/log/nginx/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload nginx
    endscript
}
EOF

# 15. Final checks
log_info "Performing final checks..."

# Check services
if systemctl is-active --quiet "$SERVICE_NAME"; then
    log_info "✅ Gunicorn service is running"
else
    log_error "❌ Gunicorn service is not running"
fi

if systemctl is-active --quiet nginx; then
    log_info "✅ Nginx service is running"
else
    log_error "❌ Nginx service is not running"
fi

if systemctl is-active --quiet redis-server; then
    log_info "✅ Redis service is running"
else
    log_error "❌ Redis service is not running"
fi

# Test application
log_info "Testing application..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    log_info "✅ Application health check passed"
else
    log_error "❌ Application health check failed"
fi

echo ""
echo "🎯 Deployment completed!"
echo "========================"
echo "📋 Next steps:"
echo "1. Update yourdomain.com in nginx.conf"
echo "2. Update SSL certificate with your actual domain"
echo "3. Update .env with your production values"
echo "4. Configure DNS to point to your server"
echo "5. Test the application at https://yourdomain.com"
echo ""
echo "📚 Useful commands:"
echo "  Check logs: journalctl -u $SERVICE_NAME -f"
echo "  Restart app: systemctl restart $SERVICE_NAME"
echo "  Reload nginx: systemctl reload nginx"
echo "  View status: systemctl status $SERVICE_NAME"
