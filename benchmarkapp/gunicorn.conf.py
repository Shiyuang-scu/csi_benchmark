# Gunicorn configuration for Render deployment

import multiprocessing

# Bind to PORT environment variable
bind = "0.0.0.0:10000"

# Use only 1 worker to reduce memory usage
# Free tier has limited RAM, so we prioritize not running out of memory
workers = 1

# Worker class
worker_class = "sync"

# Timeout - increase for long-running 3D mesh computations
timeout = 300  # 5 minutes

# Keep-alive
keepalive = 2

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Memory management - restart worker after serving requests to prevent memory leaks
max_requests = 50
max_requests_jitter = 10
