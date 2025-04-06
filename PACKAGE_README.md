# CV-to-Job Matching System - Deployment Package

This zip file contains all the necessary files to deploy the CV-to-Job Matching System as a permanent website.

## Contents

### Core Application Files
- `app.py` - Main Flask application
- `cv_parser.py` - CV parsing module
- `job_description_parser.py` - Job description parsing module
- `matching_algorithm.py` - Matching algorithm module
- `feedback_system.py` - Feedback generation module
- `database.py` - Database functionality

### Deployment Files
- `wsgi.py` - WSGI entry point
- `Procfile` - Process file for web servers
- `requirements.txt` - Python dependencies
- `runtime.txt` - Python version specification
- `app.json` - Application metadata
- `render.yaml` - Render-specific configuration
- `gunicorn.conf.py` - Gunicorn server configuration

### Templates and Static Files
- `templates/` - HTML templates
- `uploads/` - Directory for uploaded files

### Documentation
- `README.md` - Project overview
- `DEPLOYMENT.md` - Deployment instructions
- `USER_GUIDE.md` - End-user instructions

### Testing
- `tests/` - Test scripts
- `test_deployed.py` - Script to test deployed website

## Deployment Instructions

Please refer to the `DEPLOYMENT.md` file for detailed instructions on how to deploy this application to Render.

## User Guide

After deployment, share the `USER_GUIDE.md` with end users to help them understand how to use the system.

## Testing

Use `test_deployed.py` to verify that the deployed website is functioning correctly.
