# Frontend Deployment Guide - Vercel

## Prerequisites
- GitHub account
- Vercel account (free tier available)

## Deployment Steps

### 1. Push to GitHub
```bash
cd pixci-web/frontend
git init
git add .
git commit -m "Initial frontend commit"
git remote add origin <your-github-repo-url>
git push -u origin main
```

### 2. Deploy on Vercel

#### Option A: Using Vercel CLI (Recommended)
```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
vercel

# Deploy to production
vercel --prod
```

#### Option B: Using Vercel Dashboard
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: frontend
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
5. Add Environment Variables:
   ```
   NEXT_PUBLIC_API_URL=https://pixci-backend.onrender.com/api/v1
   NEXT_PUBLIC_APP_NAME=PixCI Web
   NEXT_PUBLIC_APP_VERSION=1.0.0
   ```
6. Click "Deploy"

### 3. Get Your Frontend URL
After deployment, you'll get URLs like:
```
Production: https://pixci-web.vercel.app
Preview: https://pixci-web-git-main-username.vercel.app
```

### 4. Update Backend CORS
Update your backend environment on Render:
```env
CORS_ORIGINS=https://pixci-web.vercel.app,https://pixci-web-git-main-username.vercel.app
```

## Important Notes

### Free Tier Features
- Unlimited deployments
- Automatic HTTPS
- Global CDN
- Preview deployments for every push
- 100GB bandwidth/month

### Environment Variables
Set different values for:
- **Production**: Main branch deployments
- **Preview**: Pull request deployments
- **Development**: Local development

Example:
```env
# Production
NEXT_PUBLIC_API_URL=https://pixci-backend.onrender.com/api/v1

# Preview
NEXT_PUBLIC_API_URL=https://pixci-backend-preview.onrender.com/api/v1

# Development
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### Custom Domain
1. Go to project settings
2. Click "Domains"
3. Add your domain (e.g., pixci.com)
4. Update DNS records:
   ```
   Type: CNAME
   Name: @
   Value: cname.vercel-dns.com
   ```

## Automatic Deployments

### Production Deployments
Every push to `main` branch triggers production deployment:
```bash
git add .
git commit -m "Update frontend"
git push origin main
```

### Preview Deployments
Every pull request gets a unique preview URL:
```bash
git checkout -b feature/new-feature
git add .
git commit -m "Add new feature"
git push origin feature/new-feature
# Create PR on GitHub → Automatic preview deployment
```

## Performance Optimization

### Image Optimization
Next.js automatically optimizes images:
```tsx
import Image from 'next/image'

<Image 
  src="/logo.png" 
  width={200} 
  height={200}
  alt="Logo"
/>
```

### Edge Functions
Deploy API routes to edge:
```ts
export const config = {
  runtime: 'edge',
}
```

### Analytics
Enable Vercel Analytics:
1. Go to project settings
2. Click "Analytics"
3. Enable Web Analytics
4. Add to your app:
```tsx
import { Analytics } from '@vercel/analytics/react'

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <Analytics />
      </body>
    </html>
  )
}
```

## Monitoring

### Deployment Logs
View logs in Vercel Dashboard:
- Go to your project
- Click "Deployments"
- Click on any deployment
- View build and runtime logs

### Real-time Logs
```bash
vercel logs <deployment-url>
```

### Performance Metrics
Vercel provides:
- Core Web Vitals
- Page load times
- API response times
- Error tracking

## Troubleshooting

### Build Fails
- Check build logs in Vercel dashboard
- Verify all dependencies in package.json
- Test build locally: `npm run build`

### Environment Variables Not Working
- Prefix with `NEXT_PUBLIC_` for client-side access
- Redeploy after adding variables
- Check variable names (case-sensitive)

### CORS Errors
- Verify backend CORS_ORIGINS includes your Vercel URL
- Check API_URL environment variable
- Test API endpoint directly

### 404 Errors
- Check Next.js routing
- Verify file structure in `app/` directory
- Check vercel.json configuration

## CI/CD Pipeline

### GitHub Integration
Vercel automatically:
1. Detects push to GitHub
2. Builds the project
3. Runs tests (if configured)
4. Deploys to production/preview
5. Comments on PR with preview URL

### Build Configuration
Create `vercel.json` for custom config:
```json
{
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "nextjs"
}
```

## Rollback
If deployment fails:
1. Go to "Deployments" tab
2. Find previous successful deployment
3. Click "..." menu
4. Click "Promote to Production"

## Cost Optimization

### Free Tier Limits
- 100GB bandwidth/month
- 100GB-hours serverless function execution
- 1000 image optimizations

### Upgrade to Pro ($20/month)
- 1TB bandwidth
- Unlimited team members
- Advanced analytics
- Password protection
- Custom deployment protection
