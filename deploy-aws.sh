#!/bin/bash

# AWS Deployment Script for HomeChefs AI
# This script deploys the Django app to AWS EC2 with RDS PostgreSQL

set -e

# Configuration
EC2_USER="ubuntu"
EC2_IP="your-ec2-public-ip"
PROJECT_NAME="homechefs_ai"
PROJECT_DIR="/home/$EC2_USER/$PROJECT_NAME"
PYTHON_VERSION="python3.10"

echo "🚀 Starting AWS deployment for HomeChefs AI..."

# Function to run commands on EC2
run_on_ec2() {
    ssh -o StrictHostKeyChecking=no $EC2_USER@$EC2_IP "$1"
}

# Function to copy files to EC2
copy_to_ec2() {
    scp -o StrictHostKeyChecking=no $1 $EC2_USER@$EC2_IP:$2
}

echo "📦 Installing dependencies on EC2..."
run_on_ec2 "
    sudo apt update && sudo apt upgrade -y
    sudo apt install -y software-properties-common
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt update
    sudo apt install -y $PYTHON_VERSION $PYTHON_VERSION-venv $PYTHON_VERSION-dev
    sudo apt install -y postgresql postgresql-contrib
    sudo apt install -y nginx
    sudo apt install -y redis-server
    sudo apt install -y git curl wget
"

echo "🐍 Setting up Python environment..."
run_on_ec2 "
    cd $PROJECT_DIR
    $PYTHON_VERSION -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
"

echo "📁 Creating project directory and copying files..."
run_on_ec2 "mkdir -p $PROJECT_DIR"
copy_to_ec2 "./*" "$PROJECT_DIR/"
copy_to_ec2 "requirements-prod.txt" "$PROJECT_DIR/"

echo "🔧 Installing Python dependencies..."
run_on_ec2 "
    cd $PROJECT_DIR
    source venv/bin/activate
    pip install -r requirements-prod.txt
"

echo "🗄️ Setting up PostgreSQL..."
run_on_ec2 "
    sudo -u postgres createuser $EC2_USER
    sudo -u postgres createdb $PROJECT_NAME
    sudo -u postgres psql -c \"ALTER USER $EC2_USER WITH PASSWORD 'your_db_password';\"
    sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE $PROJECT_NAME TO $EC2_USER;\"
"

echo "🔧 Configuring environment variables..."
cat > /tmp/env_config << EOF
# Production Environment Variables
SECRET_KEY=\$(openssl rand -base64 32)
DEBUG=False
ALLOWED_HOSTS=$EC2_IP,homechefhub.in,www.homechefhub.in
DATABASE_URL=postgres://$EC2_USER:your_db_password@localhost:5432/$PROJECT_NAME
REDIS_URL=redis://localhost:6379/1
EOF

copy_to_ec2 "/tmp/env_config" "$PROJECT_DIR/.env"
run_on_ec2 "
    cd $PROJECT_DIR
    mv .env .env.production
    chmod 600 .env.production
"

echo "🗃️ Running Django migrations and collecting static files..."
run_on_ec2 "
    cd $PROJECT_DIR
    source venv/bin/activate
    export DJANGO_SETTINGS_MODULE=HomeChefs.settings_production
    python manage.py migrate
    python manage.py collectstatic --noinput
    python manage.py createsuperuser --noinput --username admin --email admin@homechefhub.in || true
"

echo "🌐 Configuring Nginx..."
cat > /tmp/nginx_config << EOF
server {
    listen 80;
    server_name $EC2_IP homechefhub.in www.homechefhub.in;
    
    client_max_body_size 20M;
    
    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
        expires 30d;
        add_header Cache-Control \"public, immutable\";
    }
    
    location /media/ {
        alias $PROJECT_DIR/media/;
        expires 30d;
        add_header Cache-Control \"public, immutable\";
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

copy_to_ec2 "/tmp/nginx_config" "/tmp/homechefs_nginx"
run_on_ec2 "
    sudo mv /tmp/homechefs_nginx /etc/nginx/sites-available/homechefs
    sudo ln -sf /etc/nginx/sites-available/homechefs /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    sudo nginx -t && sudo systemctl reload nginx
"

echo "🔧 Configuring Gunicorn service..."
cat > /tmp/gunicorn_service << EOF
[Unit]
Description=HomeChefs AI Gunicorn daemon
After=network.target

[Service]
User=$EC2_USER
Group=$EC2_USER
WorkingDirectory=$PROJECT_DIR
Environment=\"PATH=$PROJECT_DIR/venv/bin\"
EnvironmentFile=$PROJECT_DIR/.env.production
ExecStart=$PROJECT_DIR/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 HomeChefs.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

copy_to_ec2 "/tmp/gunicorn_service" "/tmp/homechefs_gunicorn"
run_on_ec2 "
    sudo mv /tmp/homechefs_gunicorn /etc/systemd/system/homechefs.service
    sudo systemctl daemon-reload
    sudo systemctl enable homechefs
    sudo systemctl start homechefs
"

echo "🔧 Configuring Redis..."
run_on_ec2 "
    sudo systemctl enable redis-server
    sudo systemctl start redis-server
"

echo "🔥 Setting up UFW firewall..."
run_on_ec2 "
    sudo ufw allow ssh
    sudo ufw allow 'Nginx Full'
    sudo ufw --force enable
"

echo "📊 Setting up monitoring..."
run_on_ec2 "
    sudo systemctl status homechefs
    sudo systemctl status nginx
    sudo systemctl status redis-server
"

echo "✅ Deployment completed successfully!"
echo "🌐 Your app should be available at: http://$EC2_IP"
echo "🔧 Next steps:"
echo "   1. Configure DNS for homechefhub.in to point to $EC2_IP"
echo "   2. Set up SSL certificate with Let's Encrypt"
echo "   3. Configure AWS S3 for media storage"
echo "   4. Set up AWS RDS for production database"
echo "   5. Configure AWS CloudFront for CDN"

# Clean up temporary files
rm -f /tmp/env_config /tmp/nginx_config /tmp/gunicorn_service

echo "🎉 HomeChefs AI deployment complete!"
