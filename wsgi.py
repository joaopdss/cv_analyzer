"""
Deployment configuration for the CV-to-Job Matching System.
This file prepares the application for deployment using Gunicorn.
"""

import os
from app import app

# Explicitly set the port for Render to detect
port = int(os.environ.get('PORT', 10000))

if __name__ == "__main__":
    # Run the app with Gunicorn when deployed
    app.run(host='0.0.0.0', port=port)
