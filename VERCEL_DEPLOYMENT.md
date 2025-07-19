# Vercel Deployment Guide for SmartShop

## Overview
This guide will help you deploy your SmartShop application to Vercel. The deployment includes:
- Backend API (FastAPI) on Vercel Functions
- Frontend (React/Vite) on Vercel Static Hosting

## Prerequisites
1. Vercel account (free tier available)
2. GitHub repository with your code
3. Vercel CLI (optional but recommended)

## Step 1: Prepare Your Repository

### Backend Preparation
The backend has been configured for Vercel with:
- `vercel.json` - Vercel configuration
- `requirements-vercel.txt` - Vercel-compatible dependencies
- `api/index.py` - Serverless function entry point

### Frontend Preparation
The frontend is already Vercel-compatible with:
- `frontend/vercel.json` - Frontend configuration
- Vite build configuration

## Step 2: Deploy Backend API

### Option A: Deploy via Vercel Dashboard
1. Go to [vercel.com](https://vercel.com) and sign in
2. Click "New Project"
3. Import your GitHub repository
4. Configure the project:
   - **Framework Preset**: Other
   - **Root Directory**: `./` (root of your project)
   - **Build Command**: Leave empty (Vercel will auto-detect)
   - **Output Directory**: Leave empty
   - **Install Command**: `pip install -r requirements-vercel.txt`

### Option B: Deploy via Vercel CLI
```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy from project root
vercel

# Follow the prompts:
# - Set up and deploy: Yes
# - Which scope: Your account
# - Link to existing project: No
# - Project name: smartshop-backend
# - Directory: ./ (current directory)
```

### Environment Variables
Set these in Vercel dashboard:
```
OPENAI_API_KEY=your_openai_api_key
JWT_SECRET=your_jwt_secret
DEBUG=false
```

## Step 3: Deploy Frontend

### Option A: Deploy via Vercel Dashboard
1. Create another project in Vercel
2. Import the same GitHub repository
3. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm ci`

### Option B: Deploy via Vercel CLI
```bash
# Navigate to frontend directory
cd frontend

# Deploy frontend
vercel

# Follow the prompts:
# - Project name: smartshop-frontend
# - Directory: ./frontend
```

### Frontend Environment Variables
Set in Vercel dashboard:
```
VITE_API_URL=https://your-backend-url.vercel.app
```

## Step 4: Update CORS Configuration

After deployment, update your backend CORS origins to include your frontend URL:

```python
# In app/core/config.py
CORS_ORIGINS: List[str] = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://your-frontend-url.vercel.app",
    "https://*.vercel.app"
]
```

## Step 5: Test Your Deployment

### Test Backend
```bash
# Test health endpoint
curl https://your-backend-url.vercel.app/health

# Test API docs
curl https://your-backend-url.vercel.app/docs
```

### Test Frontend
1. Visit your frontend URL
2. Test the search functionality
3. Check browser console for any errors

## Important Notes

### Serverless Limitations
- **Function Timeout**: 30 seconds max (configured in vercel.json)
- **Memory**: 1024MB max
- **Cold Starts**: First request may be slower

### Browser Automation
- Playwright and Selenium are **NOT supported** on Vercel
- The app uses mock scrapers for demonstration
- For production scraping, consider:
  - External scraping service
  - Alternative deployment (Railway, Heroku)
  - API-based solutions

### Database
- MongoDB connection is optional
- App works in memory-only mode
- For production database, consider:
  - MongoDB Atlas (free tier)
  - Vercel Postgres
  - External database service

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check `requirements-vercel.txt` for compatibility
   - Ensure all dependencies are serverless-compatible

2. **CORS Errors**
   - Verify CORS origins include your frontend URL
   - Check environment variables

3. **Function Timeouts**
   - Optimize code for faster execution
   - Consider breaking large operations

4. **Cold Start Delays**
   - Normal for serverless functions
   - Subsequent requests will be faster

### Debug Commands
```bash
# Check Vercel logs
vercel logs

# Redeploy with debug info
vercel --debug

# Check function status
vercel ls
```

## Cost Considerations

### Free Tier Limits
- **Functions**: 100GB-hours/month
- **Bandwidth**: 100GB/month
- **Builds**: 100 builds/day
- **Domains**: Unlimited custom domains

### Monitoring Usage
- Check Vercel dashboard for usage metrics
- Monitor function execution times
- Track bandwidth usage

## Next Steps

1. **Set up custom domain** (optional)
2. **Configure monitoring** and alerts
3. **Set up CI/CD** for automatic deployments
4. **Add database** for production use
5. **Implement real scraping** via external services

## Support

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Community](https://github.com/vercel/vercel/discussions)
- [FastAPI on Vercel](https://vercel.com/docs/functions/serverless-functions/runtimes/python)

---

**Note**: This deployment uses mock scrapers for demonstration. For production use with real scraping, consider alternative deployment options that support browser automation. 