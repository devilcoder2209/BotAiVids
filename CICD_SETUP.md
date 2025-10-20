# CI/CD Setup Guide

This guide explains how to set up automated deployment for the BotAiVids application using GitHub Actions and Render.

## What is CI/CD?

**CI/CD** stands for **Continuous Integration / Continuous Deployment**. It automates the process of testing and deploying your code whenever you make changes.

### What This Does For You

- **Automatic Quality Checks**: Every time you push code, it checks for errors
- **Automatic Deployment**: When you push to the `main` branch, your app automatically deploys to Render
- **Peace of Mind**: Know that your code works before it goes live

## Setup Instructions

### Step 1: Get Your Render Deploy Hook

A deploy hook is a special URL that GitHub will use to tell Render to deploy your app.

1. Go to your Render Dashboard: https://dashboard.render.com/
2. Click on your **botaivids-app1** service
3. Navigate to the **Settings** tab
4. Scroll down to find the **Deploy Hook** section
5. Click **"Create Deploy Hook"**
6. You'll see a URL that looks like this:
   ```
   https://api.render.com/deploy/srv-xxxxx?key=yyyyy
   ```
7. **Copy this entire URL** (you'll need it in the next step)

### Step 2: Add the Deploy Hook to GitHub

GitHub needs to know your Render deploy hook URL. For security, we store it as a "secret".

1. Go to your GitHub repository: https://github.com/devilcoder2209/BotAiVids
2. Click on **Settings** (top navigation bar)
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click the green **"New repository secret"** button
5. Fill in the form:
   - **Name**: `RENDER_DEPLOY_HOOK`
   - **Secret**: Paste the deploy hook URL you copied in Step 1
6. Click **"Add secret"**

### Step 3: Enable GitHub Actions (Usually Already Enabled)

1. In your repository, go to **Settings** → **Actions** → **General**
2. Under "Actions permissions", make sure **"Allow all actions and reusable workflows"** is selected
3. Click **Save** if you changed anything

### Step 4: Push Your Code

The CI/CD pipeline is now ready! Whenever you push code to the `main` branch, it will automatically:

1. Check your code for syntax errors
2. Verify all required files exist
3. Test that your Python imports work
4. Deploy to Render
5. Check that your app is running

```powershell
# Make your changes, then:
git add .
git commit -m "Your commit message"
git push origin main
```

## How to Monitor Deployments

### Watch Your Deployment in Real-Time

1. Go to your GitHub repository
2. Click the **Actions** tab
3. You'll see a list of workflow runs
4. Click on the latest one to see detailed logs

### Check Deployment Status

The Actions tab shows you:
- ✅ Green checkmark = Deployment successful
- ❌ Red X = Something went wrong
- 🟡 Yellow dot = Currently deploying

### View Your Live Application

After deployment completes (usually 2-3 minutes), visit:
- **Your App**: https://botaivids-app1.onrender.com

## Understanding the Workflow

The deployment process has 2 main jobs:

### Job 1: Quality Check
Before deploying, this job verifies:
- No Python syntax errors exist
- All critical files are present (app.py, main.py, requirements.txt, etc.)
- Python can import your main modules without errors

**Duration**: ~1-2 minutes

### Job 2: Deploy
This job:
- Triggers Render to start building your app
- Waits for deployment to begin
- Checks if your app is responding correctly
- Reports success or failure

**Duration**: ~2-3 minutes (plus Render build time)

## Manual Deployment

You can also trigger a deployment manually without pushing code:

1. Go to your repository's **Actions** tab
2. Click **"Deploy to Production"** in the left sidebar
3. Click **"Run workflow"** button
4. Select the `main` branch
5. Click the green **"Run workflow"** button

This is useful for:
- Re-deploying after fixing environment variables in Render
- Deploying after updating Render configuration
- Testing the deployment process

## Troubleshooting

### Deployment Failed: "RENDER_DEPLOY_HOOK secret is not configured"

**Problem**: GitHub can't find your deploy hook secret.

**Solution**:
1. Verify you added the secret with the exact name: `RENDER_DEPLOY_HOOK`
2. Check there are no spaces in the name
3. Make sure you copied the entire deploy hook URL from Render

### Deployment Triggered But App Not Responding

**Problem**: Render received the deployment request but build failed.

**Solution**:
1. Go to Render Dashboard: https://dashboard.render.com/
2. Click on your service
3. Check the **Logs** tab for build errors
4. Common issues:
   - Missing environment variables (DATABASE_URL, SECRET_KEY, etc.)
   - Database connection problems
   - FFmpeg installation issues

### Quality Check Failed

**Problem**: The quality check job found errors in your code.

**Solution**:
1. Click on the failed workflow run in GitHub Actions
2. Read the error messages in the logs
3. Fix the issues locally
4. Test by running: `python -c "import app"`
5. Commit and push again

### Health Check Timed Out

**Problem**: The deployment triggered but the health check couldn't verify the app.

**What This Means**:
- The deployment might still be in progress (Render builds can take 3-5 minutes)
- The app might be working but slow to respond initially

**What To Do**:
1. Wait a few more minutes
2. Check your app URL: https://botaivids-app1.onrender.com
3. Check Render dashboard logs if it's still not working

## Best Practices

### Before Pushing Code

1. **Test locally first**
   ```powershell
   python main.py
   # Visit http://localhost:5000 and test
   ```

2. **Check for obvious errors**
   ```powershell
   python -c "import app"
   python -c "import main"
   ```

3. **Use meaningful commit messages**
   ```powershell
   # Good examples:
   git commit -m "Fix video upload bug for large files"
   git commit -m "Add user profile page"
   git commit -m "Update database schema for new features"
   
   # Avoid:
   git commit -m "update"
   git commit -m "fix"
   ```

### Working with Branches

If you want to test changes without deploying:

1. **Create a feature branch**
   ```powershell
   git checkout -b feature/my-new-feature
   ```

2. **Make your changes and push**
   ```powershell
   git add .
   git commit -m "Add new feature"
   git push origin feature/my-new-feature
   ```

3. **Create a Pull Request on GitHub**
   - The quality checks will run
   - But deployment will NOT happen (only happens on `main` branch)

4. **Merge when ready**
   - Once you merge the PR to `main`, deployment will trigger automatically

## Environment Variables

Make sure these are set in your Render dashboard:

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `SECRET_KEY` | Flask session secret | Yes |
| `CLOUDINARY_URL` | Cloudinary API credentials | Yes |
| `ELEVENLABS_API_KEY` | ElevenLabs API key | Yes |
| `FLASK_ENV` | Set to `production` | Yes |

To update environment variables:
1. Go to Render Dashboard
2. Click your service → Settings
3. Scroll to Environment Variables
4. Click "Add Environment Variable" or edit existing ones
5. Click "Save Changes"

**Note**: After changing environment variables, you may need to manually trigger a deployment.

## Security Notes

### Keep Secrets Secret

- **Never commit** API keys or passwords to your code
- **Always use** environment variables for sensitive data
- **Never share** your deploy hook URL publicly

### The Deploy Hook is Sensitive

Anyone with your deploy hook URL can trigger deployments. If it's ever compromised:

1. Go to Render → Settings → Deploy Hook
2. Click "Delete Deploy Hook"
3. Create a new one
4. Update the `RENDER_DEPLOY_HOOK` secret in GitHub

## Understanding the Badge

You can add a status badge to your README to show deployment status:

```markdown
![Deployment Status](https://github.com/devilcoder2209/BotAiVids/actions/workflows/deploy.yml/badge.svg)
```

This badge will show:
- 🟢 **passing** = Latest deployment successful
- 🔴 **failing** = Latest deployment failed
- 🟡 **pending** = Deployment in progress

## Getting Help

If you encounter issues:

1. **Check GitHub Actions logs**: See exactly what failed
2. **Check Render logs**: See build and runtime errors
3. **Review this guide**: Make sure you followed all steps
4. **Check Render status**: https://status.render.com/

## Summary

Once set up, your workflow is simple:

```
Make changes → Commit → Push → Automatic Deployment → App Updated
```

No manual steps needed! Just push your code and let the automation handle the rest.
