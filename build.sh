#!/bin/bash
# Render build script to ensure all dependencies are properly installed

# Install Python dependencies
pip install -r requirements.txt

# Verify gunicorn is installed
echo "Verifying gunicorn installation..."
if command -v gunicorn &> /dev/null; then
    echo "✅ Gunicorn is installed: $(gunicorn --version)"
else
    echo "❌ Gunicorn installation failed. Installing directly..."
    pip install gunicorn gevent
    if command -v gunicorn &> /dev/null; then
        echo "✅ Gunicorn is now installed: $(gunicorn --version)"
    else
        echo "❌ Gunicorn installation still failed. Please check your environment."
        exit 1
    fi
fi

# Create necessary directories
mkdir -p uploads

echo "Build completed successfully!"
