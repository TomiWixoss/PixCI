# PixCI Web - Complete Deployment Guide

## Architecture Overview

```
┌─────────────────┐         ┌──────────────────┐
│   Vercel        │         │   Render         │
│   (Frontend)    │────────▶│   (Backend)      │
│   Next.js       │  HTTPS  │   FastAPI        │
└─────────────────┘         └──────────────────┘
```

## Quick Start Deployment

### 1. Backend on Render

```bash
cd pixci-web/backend

# Push to GitHub
git init
git add .
git commit -m "Backend ready for deployment"
git remote add origin <your-backend-repo-url>
git push -u origin main
```

**Deploy on Render:**
1. Go to https://dashboard.render.com/
2. Click "New" → "Blueprint"
3. Connect GitHub repo
4. Render auto-detects `render.yaml`
5. Click "Apply"
6. Wait for deployment (~5 minutes)
7. Copy your backend URL: `https://pixci-backend-xxxx.onrender.com`

### 2. Frontend on Vercel

```bash
cd pixci-web/frontend

# Update API URL in vercel.json
# Replace with your Render backend URL

# Push to GitHub
git init
git add .
git commit -m "Frontend ready for deployment"
git remote add origin <your-frontend-repo-url>
git push -u origin main
```

**Deploy on Vercel:**
1. Go to https://vercel.com/dashboard
2. Click "Add New" → "Project"
3. Import GitHub repo
4. Framework: Next.js (auto-detected)
5. Root Directory: `frontend`
6. Add Environment Variable:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.onrender.com/api/v1
   ```
7. Click "Deploy"
8. Wait for deployment (~2 minutes)
9. Your app is live! 🎉

### 3. Update Backend CORS

Go back to Render and update environment variable:
```
CORS_ORIGINS=https://your-app.vercel.app
```

## Environment Variables

### Backend (Render)
```env
HOST=0.0.0.0
PORT=8000
DEBUG=false
CORS_ORIGINS=https://your-frontend.vercel.app
MAX_UPLOAD_SIZE=10485760
MAX_IMAGE_DIMENSION=512
```

### Frontend (Vercel)
```env
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com/api/v1
NEXT_PUBLIC_APP_NAME=PixCI Web
NEXT_PUBLIC_APP_VERSION=1.0.0
```

## Docker Deployment (Alternative)

### Backend Docker
```bash
cd pixci-web/backend
docker build -t pixci-backend .
docker run -p 8000:8000 pixci-backend
```

### Frontend Docker
```bash
cd pixci-web/frontend
docker build -t pixci-frontend .
docker run -p 3000:3000 pixci-frontend
```

### Docker Compose
```bash
cd pixci-web
docker-compose up -d
```

## Cost Breakdown

### Free Tier (Recommended for Testing)
- **Render Free**: Backend hosting
  - 750 hours/month
  - Spins down after 15 min inactivity
  - 512MB RAM
- **Vercel Free**: Frontend hosting
  - 100GB bandwidth/month
  - Unlimited deployments
  - Global CDN

**Total: $0/month**

### Production Tier
- **Render Starter**: $7/month
  - No spin-down
  - 512MB RAM
  - Better performance
- **Vercel Pro**: $20/month
  - 1TB bandwidth
  - Advanced analytics
  - Team features

**Total: $27/month**

## Monitoring & Logs

### Backend (Render)
- Logs: https://dashboard.render.com → Your Service → Logs
- Health: `https://your-backend.onrender.com/api/v1/health`
- API Docs: `https://your-backend.onrender.com/api/docs`

### Frontend (Vercel)
- Deployments: https://vercel.com/dashboard → Your Project
- Analytics: Enable in project settings
- Logs: `vercel logs <deployment-url>`

## CI/CD Pipeline

Both platforms auto-deploy on git push:

```bash
# Make changes
git add .
git commit -m "Update feature"
git push

# Automatic deployment triggers:
# - Render rebuilds backend
# - Vercel rebuilds frontend
# - Zero-downtime deployment
```

## Custom Domains

### Backend (Render)
1. Go to service settings
2. Add custom domain: `api.yourdomain.com`
3. Update DNS:
   ```
   Type: CNAME
   Name: api
   Value: <render-provided-value>
   ```

### Frontend (Vercel)
1. Go to project settings → Domains
2. Add domain: `yourdomain.com`
3. Update DNS:
   ```
   Type: CNAME
   Name: @
   Value: cname.vercel-dns.com
   ```

## Troubleshooting

### Backend Issues
- **Build fails**: Check Dockerfile and requirements.txt
- **Service won't start**: Verify environment variables
- **CORS errors**: Update CORS_ORIGINS with frontend URL

### Frontend Issues
- **Build fails**: Run `npm run build` locally first
- **API errors**: Check NEXT_PUBLIC_API_URL
- **404 errors**: Verify Next.js routing

### Common Fixes
```bash
# Clear cache and rebuild
rm -rf .next node_modules
npm install
npm run build

# Check environment variables
vercel env ls
```

## Security Checklist

- [ ] Set DEBUG=false in production
- [ ] Use HTTPS only (automatic on Render/Vercel)
- [ ] Limit CORS_ORIGINS to your domain
- [ ] Set MAX_UPLOAD_SIZE appropriately
- [ ] Enable rate limiting (add middleware)
- [ ] Use environment variables for secrets
- [ ] Enable Vercel password protection (Pro plan)

## Performance Tips

### Backend
- Use Render Starter plan (no spin-down)
- Enable caching for static responses
- Optimize image processing
- Add Redis for session storage

### Frontend
- Enable Vercel Analytics
- Use Next.js Image optimization
- Implement lazy loading
- Enable edge functions for API routes

## Support

- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **Next.js Docs**: https://nextjs.org/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com/

## Rollback

### Render
1. Go to Deploys tab
2. Find previous successful deploy
3. Click "Rollback"

### Vercel
1. Go to Deployments
2. Find previous deployment
3. Click "..." → "Promote to Production"
