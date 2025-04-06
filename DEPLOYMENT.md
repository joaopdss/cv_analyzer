# CV-to-Job Matching System - Deployment Guide

This guide provides instructions for deploying the CV-to-Job Matching System to Render.

## Prerequisites

Before deploying, make sure you have:

1. A Render account (sign up at https://render.com if you don't have one)
2. A GitHub account to host your repository

## Deployment Steps

### 1. Create a GitHub Repository

1. Create a new GitHub repository for your project
2. Push your code to the repository:
   ```
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/cv-job-matching.git
   git push -u origin main
   ```

### 2. Deploy to Render

1. Log in to your Render account
2. Click on "New" and select "Web Service"
3. Connect your GitHub repository
4. Configure the web service:
   - **Name**: cv-job-matching
   - **Environment**: Python
   - **Region**: Choose the region closest to your users
   - **Branch**: main (or your default branch)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn wsgi:app`
   - **Plan**: Free (or select a paid plan for production use)

5. Click "Create Web Service"

### 3. Environment Variables

After deployment, set up the following environment variables in the Render dashboard:

- **SECRET_KEY**: A secure random string for Flask sessions
- **DATABASE_URL**: Path to your database (Render will provide this if using their database service)

### 4. Database Setup

For production, consider using Render's PostgreSQL database:

1. In the Render dashboard, go to "New" and select "PostgreSQL"
2. Configure your database settings
3. After creation, Render will provide a connection string
4. Add this connection string as the DATABASE_URL environment variable

## Accessing Your Deployed Application

Once deployed, your application will be available at:
```
https://cv-job-matching.onrender.com
```

Replace "cv-job-matching" with the name you chose during deployment.

## Troubleshooting

If you encounter issues during deployment:

1. Check the Render logs in the dashboard
2. Verify that all required files are in your repository
3. Ensure your requirements.txt includes all dependencies
4. Check that your database configuration is correct

## Maintenance

To update your deployed application:

1. Push changes to your GitHub repository
2. Render will automatically deploy the new version

For manual deployments, you can use the "Manual Deploy" button in the Render dashboard.
