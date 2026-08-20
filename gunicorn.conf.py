# Gunicorn configuration for HomeChefs AI
# Production web server configuration

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"

# Worker processes (2 * CPU cores + 1)
workers = multiprocessing.cpu_count() * 2 + 1

# Worker class
worker_class = "sync"

# Worker connections
worker_connections = 1000

# Maximum requests per worker
max_requests = 1000

# Maximum request time (seconds)
timeout = 30

# Keep workers alive
keepalive = 5

# Loading mechanism
preload_app = True

# User and group
user = os.getenv('GUNICORN_USER', 'www-data')
group = os.getenv('GUNICORN_GROUP', 'www-data')

# Temporary directory
tmp_upload_dir = None

# Logging
accesslog = os.getenv('GUNICORN_ACCESS_LOG', '/var/log/gunicorn/access.log')
errorlog = os.getenv('GUNICORN_ERROR_LOG', '/var/log/gunicorn/error.log')
loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'info')

# Process naming
proc_name = 'homechefs_ai'

# Security
limit_request_line = 4096

# Graceful timeout
graceful_timeout = 30

# Django WSGI application
wsgi_app = 'HomeChefs.wsgi:application'

# Raw environment
raw_env = [
    ('DJANGO_SETTINGS_MODULE', 'HomeChefs.settings'),
]

# SSL configuration (uncomment for HTTPS)
# keyfile = '/path/to/ssl/private.key'
# certfile = '/path/to/ssl/certificate.crt'
