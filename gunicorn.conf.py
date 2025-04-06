"""
Gunicorn configuration file for the CV-to-Job Matching System.
This file contains settings for the Gunicorn WSGI server.
"""

import os

# Bind to 0.0.0.0 to ensure the application is accessible externally
# Use PORT environment variable or default to 10000
port = os.environ.get('PORT', '10000')
bind = f"0.0.0.0:{port}"

# Number of worker processes
workers = 4

# Use gevent worker type for better performance with async operations
worker_class = "gevent"

# Timeout for worker processes (in seconds)
timeout = 120

# Maximum number of requests a worker will process before restarting
max_requests = 1000
max_requests_jitter = 50

# Log level
loglevel = "info"

# Access log format
accesslog = "-"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Error log
errorlog = "-"

# Preload application code before forking worker processes
preload_app = True

# Restart workers when code changes (development only)
reload = False
