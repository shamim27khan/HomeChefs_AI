# AWS Deployment Guide for HomeChefs AI

This guide provides step-by-step instructions for deploying HomeChefs AI to AWS with cost optimization for startups.

## 📋 Prerequisites

- AWS account with billing enabled
- Domain name (homechefhub.in)
- GitHub repository
- Basic knowledge of AWS services

## 🏗️ Architecture Overview

### Phase 1: MVP Launch (₹2,500-4,000/month)
- **Compute**: EC2 t3.micro (Free tier eligible)
- **Database**: RDS PostgreSQL db.t3.micro (Free tier eligible)
- **Storage**: S3 Standard for media files
- **CDN**: CloudFront for static assets
- **SSL**: AWS Certificate Manager (Free)

### Phase 2: Growth Stage (₹8,000-15,000/month)
- **Compute**: EC2 t3.small + Application Load Balancer
- **Database**: RDS PostgreSQL db.t3.small with Multi-AZ
- **Cache**: ElastiCache Redis
- **Monitoring**: CloudWatch enhanced

## 🚀 Quick Start

### 1. Setup AWS Infrastructure

```bash
# Make the setup script executable
chmod +x setup-aws-infrastructure.sh

# Run the infrastructure setup
./setup-aws-infrastructure.sh
```

This script creates:
- VPC with public and private subnets
- Security groups for web and database
- RDS PostgreSQL instance
- S3 bucket for media files
- EC2 instance with key pair
- Route 53 DNS records

### 2. Configure Environment Variables

Copy the example environment file:
```bash
cp .env.production.example .env.production
```

Update `.env.production` with actual values from the infrastructure setup:
```bash
# Django Configuration
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=homechefhub.in,www.homechefhub.in

# Database Configuration (from infrastructure-details.txt)
DATABASE_URL=postgres://homechefs:password@rds-endpoint:5432/homechefs_ai

# AWS Configuration (from infrastructure-details.txt)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=homechefhub-media-xxxxx
AWS_S3_REGION_NAME=ap-south-1

# Redis Configuration (if using ElastiCache)
REDIS_URL=redis://redis-endpoint:6379/1
```

### 3. Deploy Application

```bash
# Make the deployment script executable
chmod +x deploy-aws.sh

# Update the script with your EC2 IP
# Edit deploy-aws.sh and set EC2_IP="your-ec2-public-ip"

# Run the deployment
./deploy-aws.sh
```

### 4. Setup SSL Certificate

```bash
# SSH into your EC2 instance
ssh -i ~/.ssh/homechefs-ai-keypair.pem ubuntu@your-ec2-ip

# Install Let's Encrypt
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d homechefhub.in -d www.homechefhub.in

# Setup auto-renewal
sudo crontab -e
# Add this line: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🐳 Docker Deployment (Alternative)

For containerized deployment:

```bash
# Build and run with Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Collect static files
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

## 🔄 CI/CD Pipeline

The GitHub Actions workflow automatically:

1. **Tests**: Runs unit tests and security scans
2. **Builds**: Packages the application
3. **Deploys**: 
   - Staging: On every push to main branch
   - Production: On version tags (v1.0.0, etc.)

### Required GitHub Secrets

Set these in your GitHub repository settings:

```bash
# Staging Environment
STAGING_HOST=your-staging-ec2-ip
STAGING_USER=ubuntu
STAGING_SSH_KEY=-----BEGIN OPENSSH PRIVATE KEY-----
STAGING_URL=http://staging.homechefhub.in

# Production Environment
PRODUCTION_HOST=your-production-ec2-ip
PRODUCTION_USER=ubuntu
PRODUCTION_SSH_KEY=-----BEGIN OPENSSH PRIVATE KEY-----

# Monitoring
SLACK_WEBHOOK=your-slack-webhook-url
```

## 📊 Monitoring & Logging

### Application Logs
```bash
# View application logs
sudo journalctl -u homechefs -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Database Monitoring
```bash
# Monitor RDS performance
aws rds describe-db-instances --db-instance-identifier homechefs-ai-db

# View database logs
aws rds describe-db-log-files --db-instance-identifier homechefs-ai-db
```

### Cost Monitoring
```bash
# Set up billing alerts
aws budgets create-budget \
    --account-id $(aws sts get-caller-identity --query Account --output text) \
    --budget '{
        "BudgetName": "HomeChefs-AI-Budget",
        "BudgetType": "COST",
        "TimeUnit": "MONTHLY",
        "BudgetLimit": {
            "Amount": "5000",
            "Unit": "INR"
        }
    }'
```

## 🔧 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Check RDS security group allows EC2 access
   aws ec2 describe-security-groups --group-ids sg-xxxxxxxxx
   ```

2. **Static Files Not Loading**
   ```bash
   # Check Nginx configuration
   sudo nginx -t
   sudo systemctl reload nginx
   
   # Check file permissions
   sudo chown -R www-data:www-data /home/ubuntu/homechefs_ai/staticfiles
   ```

3. **SSL Certificate Issues**
   ```bash
   # Check certificate status
   sudo certbot certificates
   
   # Renew certificate manually
   sudo certbot renew
   ```

### Performance Optimization

1. **Database Optimization**
   ```bash
   # Enable query logging in production
   # Add to settings_production.py:
   LOGGING['loggers']['django.db.backends'] = {
       'handlers': ['file'],
       'level': 'DEBUG',
       'propagate': False,
   }
   ```

2. **Caching**
   ```bash
   # Clear Redis cache
   redis-cli FLUSHALL
   
   # Monitor cache performance
   redis-cli INFO stats
   ```

## 💰 Cost Optimization Tips

1. **Use Free Tier**: Maximize AWS Free Tier benefits (12 months)
2. **Reserved Instances**: Save 40% with 1-year commitment
3. **Auto Scaling**: Scale down during off-peak hours
4. **S3 Lifecycle**: Move old files to cheaper storage tiers
5. **CloudFront**: Enable caching to reduce data transfer costs

## 🚨 Security Checklist

- [ ] Update all system packages: `sudo apt update && sudo apt upgrade`
- [ ] Configure UFW firewall: `sudo ufw enable`
- [ ] Use strong passwords and SSH keys
- [ ] Enable RDS encryption and backups
- [ ] Configure S3 bucket policies
- [ ] Set up CloudWatch alarms for security events
- [ ] Enable VPC Flow Logs
- [ ] Regular security updates

## 📞 Support

For issues:
1. Check AWS CloudWatch logs
2. Review application logs
3. Verify security group configurations
4. Test database connectivity
5. Monitor cost and usage alerts

## 🔄 Scaling Path

When traffic increases:
1. Upgrade to larger EC2 instance types
2. Add Application Load Balancer
3. Implement auto scaling
4. Add RDS read replicas
5. Enable CloudFront edge locations
6. Consider ECS Fargate for container orchestration

---

**Estimated Monthly Costs**:
- Phase 1: ₹2,500-4,000 (Free tier: ₹670)
- Phase 2: ₹8,000-15,000
- Phase 3: ₹18,000+

**Next Steps**:
1. Run infrastructure setup script
2. Configure environment variables
3. Deploy application
4. Setup SSL certificate
5. Configure monitoring and alerts
