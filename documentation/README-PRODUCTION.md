# HomeChefs AI - Production Deployment Guide

## 🚀 Production Setup Overview

This guide walks you through deploying HomeChefs AI to a production environment with all security, performance, and monitoring best practices.

## 📋 Prerequisites

- **Ubuntu 20.04+** or **CentOS 8+** server
- **Domain name** pointing to server IP
- **SSL certificate** (Let's Encrypt recommended)
- **PostgreSQL 12+** database
- **Redis 6+** for caching
- **2GB+ RAM** and **2+ CPU cores**

## 🔧 Step 1: Environment Configuration

### 1.1 Clone and Setup
```bash
git clone <your-repo-url> homechefs_ai
cd homechefs_ai
chmod +x setup-production.sh deploy-production.sh
```

### 1.2 Environment Variables
```bash
# Copy environment template
cp .env.example .env

# IMPORTANT: Update .env with your production values:
nano .env
```

**Required .env variables:**
- `SECRET_KEY`: Generate with `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string  
- `ALLOWED_HOSTS`: Your domain names
- `EMAIL_*`: SMTP configuration for notifications

## 🗄️ Step 2: Database Setup

### 2.1 PostgreSQL Installation
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# CentOS/RHEL
sudo yum install postgresql-server postgresql-contrib
```

### 2.2 Database Creation
```bash
# Run setup script
sudo -u postgres psql -f setup-database.sql

# Or manually:
sudo -u postgres psql
CREATE DATABASE homechefs_db;
CREATE USER homechefs_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE homechefs_db TO homechefs_user;
```

## 📦 Step 3: Application Setup

### 3.1 Python Environment
```bash
# Install production dependencies
pip install -r requirements-prod.txt

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
```

### 3.2 Database Migration
```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

## 🌐 Step 4: Web Server Setup

### 4.1 Gunicorn Configuration
The `gunicorn.conf.py` file is pre-configured with:
- **Worker processes**: `CPU cores * 2 + 1`
- **Timeout**: 30 seconds
- **Security**: Proper user/group permissions
- **Logging**: Structured access/error logs

### 4.2 Nginx Configuration
The `nginx.conf` file includes:
- **HTTPS redirect** (HTTP → HTTPS)
- **SSL configuration** with modern ciphers
- **Security headers** (HSTS, XSS protection, etc.)
- **Static file serving** with caching
- **Rate limiting** and connection limits
- **Health checks** for monitoring

## 🔒 Step 5: Security Setup

### 5.1 SSL Certificate
```bash
# Automatic with Let's Encrypt
sudo certbot --nginx -d yourdomain.com --email admin@yourdomain.com

# Manual upload (if using custom certificate)
# Upload certificates to /etc/ssl/ and update nginx.conf
```

### 5.2 Firewall Configuration
```bash
# UFW (Ubuntu)
sudo ufw enable
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS

# Firewalld (CentOS)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

## 🚀 Step 6: Deployment

### 6.1 Automated Deployment
```bash
# Run the deployment script
sudo ./deploy-production.sh
```

### 6.2 Manual Deployment Steps
The deployment script performs these actions:

1. **System Updates**: Updates packages
2. **Dependencies**: Installs required software
3. **Database**: Sets up PostgreSQL and Redis
4. **Application**: Installs Python packages and runs migrations
5. **Services**: Configures Gunicorn and Nginx
6. **SSL**: Sets up Let's Encrypt certificate
7. **Security**: Configures firewall and log rotation
8. **Testing**: Performs health checks

## 📊 Step 7: Monitoring & Maintenance

### 7.1 Service Management
```bash
# Check service status
systemctl status homechefs_ai    # Application
systemctl status nginx             # Web server
systemctl status redis-server        # Cache

# View logs
journalctl -u homechefs_ai -f      # Application logs
tail -f /var/log/nginx/access.log   # Web server logs
```

### 7.2 Performance Monitoring
The application includes:
- **Rate limiting**: 100 requests/minute per IP
- **Logging**: Structured logs with rotation
- **Health checks**: `/health` endpoint
- **Error tracking**: Email notifications for critical errors

### 7.3 Database Maintenance
```bash
# Backup database
pg_dump homechefs_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Optimize database
python manage.py dbshell --command "VACUUM ANALYZE;"
```

## 🔧 Configuration Files

### Production Files Created:
- `.env` - Environment variables
- `gunicorn.conf.py` - Application server config
- `nginx.conf` - Reverse proxy config
- `setup-database.sql` - Database setup
- `deploy-production.sh` - Automated deployment
- `requirements-prod.txt` - Production dependencies

### Key Settings:
- **DEBUG=False** in production
- **SECURE_* headers** enabled
- **Rate limiting** active
- **Logging** to files and console
- **Session security** enabled

## 🎯 Production Checklist

Before going live, verify:

- [ ] **Environment variables** configured in `.env`
- [ ] **Database** created and accessible
- [ ] **Redis** running and accessible
- [ ] **SSL certificate** installed and valid
- [ ] **Domain DNS** pointing to server
- [ ] **Firewall** properly configured
- [ ] **Services** running and enabled
- [ ] **Health checks** passing
- [ ] **Monitoring** configured
- [ ] **Backup strategy** in place
- [ ] **Load testing** performed

## 🚨 Troubleshooting

### Common Issues:

#### Application Not Starting
```bash
# Check logs
journalctl -u homechefs_ai -n 50

# Check configuration
python manage.py check --deploy
```

#### Database Connection Issues
```bash
# Test connection
python manage.py dbshell

# Check PostgreSQL status
systemctl status postgresql
```

#### SSL Certificate Issues
```bash
# Test certificate
openssl x509 -in /etc/letsencrypt/live/yourdomain.com/cert.pem -text -noout

# Renew certificate
sudo certbot renew
```

## 📚 Additional Resources

- **Django Deployment**: https://docs.djangoproject.com/en/stable/howto/deployment/
- **Gunicorn Documentation**: https://docs.gunicorn.org/en/stable/
- **Nginx Configuration**: https://nginx.org/en/docs/
- **PostgreSQL Performance**: https://wiki.postgresql.org/wiki/Tuning_Your_PostgreSQL_Server
- **Redis Configuration**: https://redis.io/documentation

## 🆘 Support

For production deployment issues:
1. Check application logs: `journalctl -u homechefs_ai -f`
2. Verify configuration: `python manage.py check --deploy`
3. Test database connection: `python manage.py dbshell`
4. Monitor system resources: `htop`, `df -h`, `free -m`

---

**🎉 Your HomeChefs AI application is now production-ready with enterprise-grade security, performance, and monitoring!**
