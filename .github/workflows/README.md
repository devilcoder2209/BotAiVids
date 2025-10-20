# GitHub Actions Workflows

This directory contains automated workflows for the BotAiVids application.

## Available Workflows

### deploy.yml - Production Deployment

**Triggers**:
- Automatically when code is pushed to the `main` branch
- Manually from the GitHub Actions tab

**What It Does**:
1. **Quality Check** - Verifies code quality and checks for errors
2. **Deploy** - Triggers deployment to Render
3. **Health Check** - Confirms the application is running

**Duration**: Approximately 3-5 minutes total

## Workflow File Structure

### Jobs Overview

```
quality-check (Job 1)
├── Checkout code
├── Set up Python 3.10
├── Install dependencies
├── Check for syntax errors
├── Verify required files exist
└── Test Python imports

deploy (Job 2, runs after Job 1)
├── Checkout code
├── Trigger Render deployment
├── Wait for deployment to start
├── Check application health
└── Display deployment summary
```

## Configuration

### Required Secrets

These must be configured in GitHub repository settings:

- **RENDER_DEPLOY_HOOK**: The deploy hook URL from Render
  - Location to add: Settings → Secrets and variables → Actions → New repository secret
  - How to get: Render Dashboard → Your Service → Settings → Deploy Hook

### Environment Variables

The workflow uses:
- `PYTHON_VERSION`: Set to '3.10' (matches production environment)

## How to Modify

### Change Python Version

Edit `deploy.yml`:
```yaml
env:
  PYTHON_VERSION: '3.11'  # Change to desired version
```

### Add Additional Checks

Add a new step under `quality-check` job:
```yaml
- name: Your new check
  run: |
    # Your commands here
```

### Modify Health Check Timeout

Edit the `MAX_ATTEMPTS` in the health check step:
```yaml
MAX_ATTEMPTS=10  # Change to desired number of attempts
# Each attempt waits 15 seconds, so 10 attempts = 150 seconds
```

### Change Deployment Trigger

To deploy from multiple branches, modify:
```yaml
on:
  push:
    branches: [ main, staging ]  # Add more branches
```

## Monitoring Deployments

### View Workflow Runs
1. Go to repository → Actions tab
2. Click on a workflow run to see details
3. Click on a job to see step-by-step logs

### Workflow Status
- ✅ Green = All steps passed
- ❌ Red = At least one step failed
- 🟡 Yellow = Currently running
- ⚪ Gray = Waiting or skipped

## Manual Deployment

You can manually trigger deployment:

1. Go to Actions tab
2. Select "Deploy to Production" workflow
3. Click "Run workflow"
4. Choose branch (usually `main`)
5. Click green "Run workflow" button

This is useful when:
- You updated Render environment variables
- You want to redeploy without code changes
- You're testing the deployment process

## Troubleshooting Workflows

### Workflow Not Running

**Check**:
- Is the workflow file in `.github/workflows/` directory?
- Is the file named with `.yml` or `.yaml` extension?
- Are GitHub Actions enabled? (Settings → Actions → General)

### Quality Check Failing

**Common Causes**:
- Python syntax errors in code
- Missing required files (app.py, main.py, etc.)
- Import errors due to missing dependencies

**How to Fix**:
1. Read the error logs in the failed step
2. Test imports locally: `python -c "import app"`
3. Fix the issues and push again

### Deploy Job Not Running

**Possible Reasons**:
- Quality check failed (deploy won't run if quality check fails)
- Push was to a branch other than `main`
- Deploy job is configured to skip on certain conditions

**Check**:
- Did quality check pass?
- Are you on the `main` branch?

### Deployment Triggered But Failed

**Causes**:
- Missing or incorrect `RENDER_DEPLOY_HOOK` secret
- Render service is paused or deleted
- Network connectivity issues

**How to Fix**:
1. Verify secret is set correctly in GitHub
2. Check Render dashboard to ensure service is active
3. Try manual deployment to test

## Best Practices

### Commit Messages
Use clear, descriptive commit messages:
```
✅ Good: "Add image upload validation to prevent large files"
✅ Good: "Fix database connection timeout issue"
❌ Avoid: "update"
❌ Avoid: "fix bug"
```

### Testing Before Push
Always test locally before pushing:
```powershell
# Test imports
python -c "import app"
python -c "import main"

# Run the application
python main.py

# Test in browser
# Visit http://localhost:5000
```

### Branch Strategy
- `main` branch = Production code (auto-deploys)
- Feature branches = Development (no auto-deploy)
- Create Pull Requests to merge features into main

### Monitoring
- Check Actions tab after pushing
- Wait for green checkmarks before considering deploy successful
- If red X appears, click it to see what failed

## Workflow Metrics

Typical execution times:
- **Checkout code**: 5-10 seconds
- **Set up Python**: 10-20 seconds
- **Install dependencies**: 30-60 seconds (cached)
- **Quality checks**: 20-30 seconds
- **Trigger deployment**: 5 seconds
- **Health check**: 30-150 seconds
- **Total**: 3-5 minutes

## Security Considerations

### Secrets Management
- Never hardcode sensitive values in workflow files
- Always use GitHub secrets for API keys and deploy hooks
- Secrets are encrypted and not visible in logs

### Permissions
The workflow has permissions to:
- Read repository code
- Trigger Render deployments
- Post status checks

It cannot:
- Modify repository settings
- Access other repositories
- Perform destructive operations

## Extending the Workflow

### Add Testing
To add automated tests:
```yaml
- name: Run tests
  run: |
    pip install pytest
    pytest tests/
```

### Add Code Linting
To enforce code style:
```yaml
- name: Lint with flake8
  run: |
    pip install flake8
    flake8 . --count --max-line-length=127 --statistics
```

### Add Notifications
To get notified of deployment results, you can integrate:
- Slack notifications
- Discord webhooks
- Email alerts
- GitHub Discussions posts

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Render Deploy Hooks](https://render.com/docs/deploy-hooks)
- [Workflow Syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)

## Quick Reference

| Task | Command/Action |
|------|----------------|
| View workflows | Go to Actions tab in repository |
| Trigger manual deploy | Actions → Deploy to Production → Run workflow |
| Add secret | Settings → Secrets and variables → Actions |
| Check logs | Actions → Click workflow run → Click job |
| Disable workflow | Delete or rename the .yml file |
| Re-enable workflow | Restore or rename back to .yml |

## Need Help?

If you encounter issues with the workflows:
1. Check the detailed logs in the Actions tab
2. Review the main `CICD_SETUP.md` guide
3. Verify all secrets are configured correctly
4. Ensure Render service is active and accessible
