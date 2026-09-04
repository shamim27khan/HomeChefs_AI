#!/bin/bash

# AWS Deployment Script for HomeChefs AI
# This script deploys the Django app to AWS EC2 with RDS PostgreSQL

set -e

# Configuration
EC2_USER="ec2-user"
EC2_IP="13.204.86.218"
PROJECT_NAME="homechefs_ai"
PROJECT_DIR="/home/$EC2_USER/$PROJECT_NAME"
PYTHON_VERSION="python3"
KEY_FILE="/tmp/homechefs-ai-keypair.pem"
echo "🚀 Starting AWS deployment for HomeChefs AI..."

# Function to run commands on EC2
run_on_ec2() {
    ssh -i "$KEY_FILE" -o StrictHostKeyChecking=no $EC2_USER@$EC2_IP "$1"
}

# Function to copy files to EC2
copy_to_ec2() {
    for src in $1; do
        scp -r -i "$KEY_FILE" -o StrictHostKeyChecking=no "$src" "$EC2_USER@$EC2_IP:$2"
    done
}

echo "📦 Installing dependencies on EC2..."
run_on_ec2 "
    sudo yum update -y
    sudo yum install -y $PYTHON_VERSION python3-pip python3-devel
    sudo yum install -y nginx
    sudo yum install -y git
"

echo "🐍 Setting up Python environment..."
run_on_ec2 "
    cd $PROJECT_DIR
    $PYTHON_VERSION -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
"

echo "📁 Creating project directory and copying files..."
run_on_ec2 "mkdir -p $PROJECT_DIR $PROJECT_DIR/logs && sudo chown -R $EC2_USER:$EC2_USER $PROJECT_DIR $PROJECT_DIR/logs"

echo "📦 Archiving tracked project files..."
git archive --format=tar.gz --output /tmp/homechefs_ai_deploy.tar.gz HEAD
scp -i "$KEY_FILE" -o StrictHostKeyChecking=no /tmp/homechefs_ai_deploy.tar.gz "$EC2_USER@$EC2_IP:$PROJECT_DIR/"
run_on_ec2 "cd $PROJECT_DIR && tar xzf homechefs_ai_deploy.tar.gz && rm -f homechefs_ai_deploy.tar.gz"
rm -f /tmp/homechefs_ai_deploy.tar.gz

run_on_ec2 "chmod 600 $PROJECT_DIR/.env.production"

echo "🔧 Installing Python dependencies..."
run_on_ec2 "
    cd $PROJECT_DIR
    source venv/bin/activate
    pip install -r requirements-prod.txt
"



echo "🗃️ Running Django migrations and collecting static files..."
run_on_ec2 "
    cd $PROJECT_DIR
    source venv/bin/activate
    set -a
    source .env.production
    set +a
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

    location /.well-known/acme-challenge/ {
        alias $PROJECT_DIR/.well-known/acme-challenge/;
    }

    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias $PROJECT_DIR/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
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
    sudo mv /tmp/homechefs_nginx /etc/nginx/conf.d/homechefs.conf
    sudo rm -f /etc/nginx/conf.d/default.conf
    sudo nginx -t && (sudo systemctl start nginx || true) && sudo systemctl reload nginx
"

echo "🔒 Setting up SSL certificate..."
run_on_ec2 "
    cd $PROJECT_DIR
    source venv/bin/activate
    pip install certbot
    CERT_FAILED=0
    if [ ! -f /etc/letsencrypt/live/homechefhub.in/fullchain.pem ]; then
        sudo $PROJECT_DIR/venv/bin/certbot certonly --webroot -w $PROJECT_DIR -d homechefhub.in --non-interactive --agree-tos --register-unsafely-without-email || CERT_FAILED=1
    fi
    echo \"certbot finished with CERT_FAILED=\$CERT_FAILED\"
"

echo "🌐 Reconfiguring Nginx for HTTPS..."
cat > /tmp/nginx_config_ssl << EOF
server {
    listen 80;
    server_name $EC2_IP homechefhub.in www.homechefhub.in;
    location /.well-known/acme-challenge/ {
        alias $PROJECT_DIR/.well-known/acme-challenge/;
    }
    location / {
        return 301 https://\$host\$request_uri;
    }
}
server {
    listen 443 ssl;
    server_name $EC2_IP homechefhub.in www.homechefhub.in;

    client_max_body_size 20M;

    ssl_certificate /etc/letsencrypt/live/homechefhub.in/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/homechefhub.in/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;

    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias $PROJECT_DIR/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
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

copy_to_ec2 "/tmp/nginx_config_ssl" "/tmp/homechefs_nginx_ssl"
run_on_ec2 "
    if sudo test -f /etc/letsencrypt/live/homechefhub.in/fullchain.pem; then
        sudo mv /tmp/homechefs_nginx_ssl /etc/nginx/conf.d/homechefs.conf
        sudo nginx -t && sudo systemctl reload nginx
    else
        echo 'SSL certificate not obtained, keeping HTTP-only config'
        rm -f /tmp/homechefs_nginx_ssl
    fi
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
Environment=PATH=$PROJECT_DIR/venv/bin
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
    sudo mkdir -p /var/log/django && sudo chown $EC2_USER:$EC2_USER /var/log/django
    sudo systemctl daemon-reload
    sudo systemctl enable homechefs
    sudo systemctl start homechefs
"


echo "🔥 Setting up firewalld..."
run_on_ec2 "
    sudo yum install -y firewalld
    sudo systemctl enable --now firewalld
    sudo firewall-cmd --permanent --add-service=ssh
    sudo firewall-cmd --permanent --add-service=http
    sudo firewall-cmd --permanent --add-service=https
    sudo firewall-cmd --reload
"

echo "📊 Setting up monitoring..."
run_on_ec2 "
    sleep 3
    sudo systemctl status homechefs
    sudo systemctl status nginx
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
rm -f /tmp/nginx_config /tmp/gunicorn_service

echo "🎉 HomeChefs AI deployment complete!"
