# Backend Deployment Guide - Render

## Prerequisites
- GitHub account
- Render account (free tier available)

## Deployment Steps

### 1. Push to GitHub
```bash
cd pixci-web/backend
git init
git add .
git commit -m "Initial backend commit"
git remote add origin <your-github-repo-url>
git push -u origin main
```

### 2. Deploy on Render

#### Option A: Using render.yaml (Recommended)
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New" → "Blueprint"
3. Connect your GitHub repository
4. Render will automatically detect `render.yaml`
5. Click "Apply" to deploy

#### Option B: Manual Setup
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: pixci-backend
   - **Region**: Singapore (or closest to you)
   - **Branch**: main
   - **Root Directory**: backend
   - **Runtime**: Docker
   - **Plan**: Free
5. Add Environment Variables:
   ```
   HOST=0.0.0.0
   PORT=8000
   DEBUG=false
   CORS_ORIGINS=https://your-frontend.vercel.app
   MAX_UPLOAD_SIZE=10485760
   MAX_IMAGE_DIMENSION=512
   ```
6. Click "Create Web Service"

### 3. Get Your Backend URL
After deployment, you'll get a URL like:
```
https://pixci-backend.onrender.com
```

### 4. Update Frontend Environment
Update your frontend `.env.local`:
```env
NEXT_PUBLIC_API_URL=https://pixci-backend.onrender.com/api/v1
```

## Important Notes

### Free Tier Limitations
- Service spins down after 15 minutes of inactivity
- First request after spin-down takes ~30 seconds
- 750 hours/month free (enough for 1 service)

### Upgrade to Paid Plan
For production use, consider upgrading to:
- **Starter Plan** ($7/month): No spin-down, better performance
- **Standard Plan** ($25/month): More resources, faster builds

### Custom Domain
1. Go to your service settings
2. Click "Custom Domain"
3. Add your domain (e.g., api.pixci.com)
4. Update DNS records as instructed

## Monitoring

### Logs
View logs in Render Dashboard:
- Go to your service
- Click "Logs" tab
- Real-time log streaming

### Health Check
Your service has a health check endpoint:
```
GET https://pixci-backend.onrender.com/api/v1/health
```

### Metrics
Render provides:
- CPU usage
- Memory usage
- Request count
- Response times

## Troubleshooting

### Build Fails
- Check Dockerfile syntax
- Verify all dependencies in requirements.txt
- Check build logs in Render dashboard

### Service Won't Start
- Check environment variables
- Verify PORT is set to 8000
- Check application logs

### CORS Errors
- Update CORS_ORIGINS environment variable
- Include your frontend URL
- Redeploy after changes

## CI/CD
Render automatically deploys when you push to GitHub:
```bash
git add .
git commit -m "Update backend"
git push
```

Render will:
1. Detect changes
2. Build new Docker image
3. Deploy automatically
4. Zero-downtime deployment

## Rollback
If deployment fails:
1. Go to service settings
2. Click "Deploys" tab
3. Find previous successful deploy
4. Click "Rollback"
