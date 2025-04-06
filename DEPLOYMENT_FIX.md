# CV-to-Job Matching System - Updated Deployment Instructions

## Fixing the "gunicorn: command not found" Error

If you encountered the error `bash: line 1: gunicorn: command not found` during deployment, follow these updated instructions to resolve the issue.

## What Caused the Error

The error occurred because Gunicorn (the WSGI HTTP server needed to run the Flask application) wasn't properly installed during the deployment process. This has been fixed in the updated deployment files by:

1. Adding Gunicorn explicitly to the requirements.txt file
2. Creating a build script that verifies Gunicorn installation
3. Updating the render.yaml configuration to use this build script

## Updated Deployment Steps

### 1. Download the Updated Files

The following files have been updated:
- `requirements.txt` - Now includes Gunicorn and Gevent
- `build.sh` - New build script to ensure proper installation
- `render.yaml` - Updated to use the build script

### 2. Update Your Repository

If you've already created a GitHub repository:

```bash
# Pull the updated files
git pull

# Or manually update the files and commit
git add requirements.txt build.sh render.yaml
git commit -m "Fix gunicorn installation issue"
git push
```

If you haven't created a repository yet, follow the original instructions in DEPLOYMENT.md but use these updated files.

### 3. Deploy to Render

If you've already attempted deployment:

1. Go to your Render dashboard
2. Select your web service
3. Click on "Manual Deploy" and select "Clear build cache & deploy"
4. This will force Render to use the updated build process

If you haven't deployed yet:

1. Follow the original instructions in DEPLOYMENT.md
2. The updated files will ensure Gunicorn is properly installed

### 4. Verify the Deployment

After deployment, check the build logs in the Render dashboard to confirm:
- The build script executed successfully
- Gunicorn was properly installed
- The application started without errors

## Troubleshooting

If you still encounter issues:

1. Check the Render logs for any error messages
2. Verify that the build.sh file has execute permissions
3. Try setting the environment variable `PYTHON_VERSION=3.10.12` in your Render dashboard

## Testing After Deployment

Once deployed successfully, use the test_deployed.py script as described in the original documentation to verify that all functionality is working correctly.
