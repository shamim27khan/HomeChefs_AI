# HomeChefs Deployment Guide
## Hosting on https://homechefhub.in from your local system

This guide will help you deploy your HomeChefs application on your local system and make it accessible via https://homechefhub.in/

## Prerequisites

- Ubuntu/Windows system with internet access
- Python 3.7+ installed
- Domain name: homechefhub.in
- Static public IP address (recommended) or Dynamic DNS service

## Step 1: Configure Environment Variables

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Generate a secure SECRET_KEY:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

3. Update `.env` file with your production values:
```env
SECRET_KEY=your-generated-secret-key
DEBUG=False
ALLOWED_HOSTS=homechefhub.in,www.homechefhub.in,127.0.0.1
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## Step 2: Install Production Dependencies

```bash
pip install gunicorn psycopg2-binary redis
```

## Step 3: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

## Step 4: Set Up Gunicorn (WSGI Server)

### Create Gunicorn systemd service file:

**For Linux:** Create `/etc/systemd/system/homechefs.service`:

```ini
[Unit]
Description=HomeChefs Gunicorn Daemon
After=network.target

[Service]
User=your_username
Group=www-data
WorkingDirectory=/path/to/HomeChefs_AI
ExecStart=/path/to/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/homechefs.sock \
          HomeChefs.wsgi:application

[Install]
WantedBy=multi-user.target
```

### Start the service:
```bash
sudo systemctl start homechefs
sudo systemctl enable homechefs
```

## Step 5: Set Up Nginx (Reverse Proxy)

### Install Nginx:
```bash
sudo apt update
sudo apt install nginx
```

### Create Nginx configuration:
Create `/etc/nginx/sites-available/homechefs`:

```nginx
server {
    listen 80;
    server_name homechefhub.in www.homechefhub.in;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /path/to/HomeChefs_AI/staticfiles;
    }

    location /media/ {
        root /path/to/HomeChefs_AI;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/homechefs.sock;
    }
}
```

### Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/homechefs /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

## Step 6: Configure DNS

### Option A: Static IP (Recommended)
1. Log into your domain registrar (where you bought homechefhub.in)
2. Go to DNS settings
3. Add an A record:
   - Type: A
   - Name: @ (or homechefhub.in)
   - Value: Your public IP address
   - TTL: 3600

### Option B: Dynamic DNS (If you have dynamic IP)
1. Use a service like No-IP or DuckDNS
2. Install their client on your system
3. Point your domain to their dynamic DNS hostname

## Step 7: Port Forwarding

1. Access your router's admin panel (usually 192.168.1.1 or 192.168.0.1)
2. Find Port Forwarding section
3. Forward port 80 to your local machine's IP
4. Forward port 443 to your local machine's IP
5. Save and restart router

## Step 8: Set Up SSL with Let's Encrypt

### Install Certbot:
```bash
sudo apt install certbot python3-certbot-nginx
```

### Obtain SSL Certificate:
```bash
sudo certbot --nginx -d homechefhub.in -d www.homechefhub.in
```

### Auto-renewal is configured automatically. Test it:
```bash
sudo certbot renew --dry-run
```

## Step 9: Update Django Settings for HTTPS

Your `.env` file should have:
```env
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## Step 10: Firewall Configuration

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## Step 11: Test Your Deployment

1. Check Gunicorn status:
```bash
sudo systemctl status homechefs
```

2. Check Nginx status:
```bash
sudo systemctl status nginx
```

3. Test locally:
```bash
curl http://localhost
```

4. Test from external network:
```bash
curl https://homechefhub.in
```

## Troubleshooting

### Application not accessible:
- Check if ports 80/443 are open: `sudo ufw status`
- Verify port forwarding is correct
- Check if your ISP blocks port 80 (some do)

### SSL issues:
- Ensure DNS propagation is complete (can take 24-48 hours)
- Check Nginx error logs: `sudo tail -f /var/log/nginx/error.log`

### Database errors:
- Ensure SQLite file has proper permissions
- Consider upgrading to PostgreSQL for production

## Security Recommendations

1. Keep your system updated: `sudo apt update && sudo apt upgrade`
2. Use strong passwords for all accounts
3. Enable fail2ban for brute-force protection
4. Regular backups of database and media files
5. Monitor logs regularly

## Monitoring

### Check application logs:
```bash
tail -f /path/to/HomeChefs_AI/logs/django.log
```

### Check Nginx access logs:
```bash
sudo tail -f /var/log/nginx/access.log
```

## Backup Strategy

Create a backup script:
```bash
#!/bin/bash
# Backup database
cp /path/to/HomeChefs_AI/db.sqlite3 /backups/db_$(date +%Y%m%d).sqlite3

# Backup media files
tar -czf /backups/media_$(date +%Y%m%d).tar.gz /path/to/HomeChefs_AI/media/
```

Set up cron job for automatic backups:
```bash
crontab -e
# Add: 0 2 * * * /path/to/backup-script.sh
```

## Performance Optimization

1. Use PostgreSQL instead of SQLite for production
2. Set up Redis for caching
3. Use CDN for static files
4. Enable gzip compression in Nginx
5. Consider using a VPS instead of home hosting for better reliability

## Alternative: Cloud Deployment

If home hosting proves unreliable, consider:
- DigitalOcean
- AWS EC2
- Google Cloud Platform
- Heroku
- Railway

These services provide built-in SSL, scaling, and better uptime guarantees.
