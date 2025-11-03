# Gunicorn configuration for production deployment
# Works for both Render.com and AWS EC2

import os
import multiprocessing

# Bind configuration
# Render.com: Use PORT environment variable
# AWS/Local: Use localhost:8000 (Nginx will proxy)
port = os.environ.get("PORT", "8000")
bind_host = "0.0.0.0" if os.environ.get("PORT") else "127.0.0.1"
bind = f"{bind_host}:{port}"

# Workers configuration
# Render free tier: 1 worker (limited RAM)
# AWS t3.small: 2 workers
# AWS t3.medium+: 4 workers
# Formula: (2 x CPU cores) + 1
workers = int(os.environ.get("GUNICORN_WORKERS", 2))

# Worker class
worker_class = "sync"

# Timeout - increase for long-running 3D mesh computations
timeout = 300  # 5 minutes

# Keep-alive
keepalive = 2

# Logging
# Render: stdout/stderr
# AWS: log files
if os.environ.get("PORT"):
    # Render.com - log to stdout/stderr
    accesslog = "-"
    errorlog = "-"
else:
    # AWS/Local - log to files
    accesslog = "logs/access.log"
    errorlog = "logs/error.log"

loglevel = "info"

# Memory management - restart worker after serving requests to prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Daemon mode
daemon = False
