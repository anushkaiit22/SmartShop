# 🚀 Complete SmartShop Deployment Guide

This guide covers deploying SmartShop to Render with comprehensive setup and troubleshooting.

## 📋 Prerequisites

### Required Software
- **Python 3.8+** (3.11.0 recommended)
- **Node.js 18+** (20.19.0 recommended)
- **npm** (10.8.2+ recommended)
- **Git** (for version control)

### Required Accounts
- **GitHub** account
- **Render** account (free)
- **OpenAI** API key
- **MongoDB** database (Atlas free tier recommended)

## 🔧 Local Setup

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd smartshop
```

### 2. Install Dependencies
```bash
# Python dependencies
pip install -r requirements.txt

# Frontend dependencies
cd frontend
npm install
cd ..
```

### 3. Environment Configuration
Create a `.env` file in the root directory:
```bash
# Application Settings
APP_NAME=SmartShop API
DEBUG=false
VERSION=1.0.0

# OpenAI API Key (required)
OPENAI_API_KEY=your_actual_openai_api_key_here

# MongoDB Settings (required)
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/smartshop
MONGODB_DB_NAME=smartshop

# JWT Settings
JWT_SECRET=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Settings
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173", "http://localhost:8000", "https://smartshop-frontend.onrender.com"]

# Production Settings
HOST=0.0.0.0
PORT=8000
```

### 4. Test Local Deployment
```bash
python test_local_deployment.py
```

## 🌐 Render Deployment

### 1. Prepare Your Repository
```bash
# Ensure all files are committed
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### 2. Deploy to Render

#### Option A: Using Blueprint (Recommended)
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Blueprint"
3. Connect your GitHub repository
4. Render will auto-detect `render.yaml`
5. Click "Apply" to deploy both services

#### Option B: Manual Deployment
1. Create Backend Service:
   - Type: Web Service
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python main.py`
   - Health Check Path: `/health`

2. Create Frontend Service:
   - Type: Static Site
   - Build Command: `cd frontend && npm ci --only=production && npm run build`
   - Publish Directory: `frontend/dist`

### 3. Environment Variables in Render

#### Backend Service Variables:
```
OPENAI_API_KEY=your_actual_openai_api_key
MONGODB_URL=your_mongodb_connection_string
JWT_SECRET=auto_generated_or_custom
DEBUG=false
HOST=0.0.0.0
PORT=8000
```

#### Frontend Service Variables:
```
VITE_API_URL=https://your-backend-service.onrender.com
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Backend Won't Start
**Symptoms:** Health check fails, service shows "Build Failed"
**Solutions:**
- Check environment variables are set correctly
- Verify MongoDB connection string
- Check logs in Render dashboard
- Ensure all dependencies are in `requirements.txt`

#### 2. Frontend Build Fails
**Symptoms:** Build process fails, static files not generated
**Solutions:**
- Check Node.js version compatibility
- Verify all frontend dependencies are installed
- Check for syntax errors in React components
- Ensure `VITE_API_URL` is set correctly

#### 3. CORS Errors
**Symptoms:** Frontend can't connect to backend API
**Solutions:**
- Update `CORS_ORIGINS` in backend environment variables
- Include your frontend URL in the CORS origins list
- Check that `VITE_API_URL` points to the correct backend URL

#### 4. Database Connection Issues
**Symptoms:** Backend starts but API calls fail
**Solutions:**
- Verify MongoDB connection string format
- Check network access (IP whitelist in MongoDB Atlas)
- Ensure database user has correct permissions
- Test connection string locally first

### Debug Commands

#### Check Backend Logs
```bash
# In Render dashboard, go to your backend service
# Click on "Logs" tab to see real-time logs
```

#### Test Backend Locally
```bash
python main.py
# Then visit http://localhost:8000/health
```

#### Test Frontend Locally
```bash
cd frontend
npm run dev
# Then visit http://localhost:5173
```

#### Check Dependencies
```bash
# Python
pip list | grep -E "(fastapi|uvicorn|pymongo)"

# Node.js
npm list --depth=0
```

## 📊 Monitoring and Maintenance

### Health Checks
- Backend: `https://your-backend.onrender.com/health`
- Frontend: `https://your-frontend.onrender.com/`

### Performance Monitoring
- Monitor response times in Render dashboard
- Check for memory leaks and CPU usage
- Review error logs regularly

### Updates and Maintenance
1. **Dependencies**: Update regularly for security patches
2. **Environment Variables**: Rotate secrets periodically
3. **Database**: Monitor storage and performance
4. **API Keys**: Keep OpenAI API key secure and monitor usage

## 🚀 Advanced Configuration

### Custom Domain Setup
1. Add custom domain in Render dashboard
2. Configure DNS records
3. Update CORS origins to include custom domain

### SSL Configuration
- Render provides automatic SSL certificates
- Custom certificates can be uploaded if needed

### Scaling Configuration
- Free tier: 750 hours/month
- Paid plans available for higher traffic
- Auto-scaling can be configured

## 📞 Support

### Render Support
- [Render Documentation](https://render.com/docs)
- [Render Community](https://community.render.com)

### Project Support
- Check GitHub issues
- Review deployment logs
- Test locally before deploying

## 🎯 Success Checklist

- [ ] Local tests pass (`python test_local_deployment.py`)
- [ ] All environment variables configured
- [ ] Database connection working
- [ ] Frontend builds successfully
- [ ] Backend health check passes
- [ ] API endpoints responding
- [ ] Frontend can connect to backend
- [ ] CORS configured correctly
- [ ] SSL certificates active
- [ ] Custom domain configured (if needed)

## 🏆 Deployment URLs

After successful deployment, your application will be available at:
- **Frontend**: `https://smartshop-frontend.onrender.com`
- **Backend**: `https://smartshop-backend.onrender.com`
- **API Docs**: `https://smartshop-backend.onrender.com/docs`

---

**Happy Deploying! 🚀** 