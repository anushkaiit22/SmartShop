# 🚀 Single Platform Deployment: Render

## Overview
This guide will help you deploy your entire SmartShop application on **Render** - one platform, completely free!

## 🎯 Why Render?
- ✅ **Single platform** for both frontend and backend
- ✅ **Completely free** tier available
- ✅ **Easy deployment** with automatic builds
- ✅ **Custom domains** supported
- ✅ **SSL certificates** included

## 📋 Prerequisites
1. GitHub repository with your code
2. Render account (free)
3. MongoDB Atlas account (free tier)
4. OpenAI API key (optional)

## 🚀 Step-by-Step Deployment

### Step 1: Prepare Your Repository
1. **Push your code to GitHub** (if not already done)
2. **Ensure all files are committed**:
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

### Step 2: Deploy to Render

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click "New +"** → **"Blueprint"**
3. **Connect your GitHub repository**
4. **Select your repository**
5. **Render will automatically detect the `render.yaml` file**
6. **Click "Apply"**

### Step 3: Configure Environment Variables

After deployment, go to each service and add these environment variables:

#### Backend Service (`smartshop-backend`)
```
OPENAI_API_KEY=sk-your-openai-key-here
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/smartshop
JWT_SECRET=your-super-secure-jwt-secret
DEBUG=false
```

#### Frontend Service (`smartshop-frontend`)
```
VITE_API_URL=https://smartshop-backend.onrender.com
```

### Step 4: Get Your URLs

After deployment, you'll get:
- **Frontend**: `https://smartshop-frontend.onrender.com`
- **Backend**: `https://smartshop-backend.onrender.com`

## 🔧 Configuration Details

### Backend Service
- **Type**: Web Service
- **Environment**: Python 3.11
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python main.py`
- **Health Check**: `/health`

### Frontend Service
- **Type**: Static Site
- **Build Command**: `cd frontend && npm install && npm run build`
- **Publish Directory**: `frontend/dist`

## 🛠️ Environment Setup

### 1. MongoDB Atlas (Free Database)
1. Go to https://www.mongodb.com/atlas
2. Create free account
3. Create new cluster
4. Get connection string
5. Add to Render environment variables

### 2. OpenAI API (Optional)
1. Go to https://platform.openai.com
2. Get API key
3. Add to Render environment variables

## 🔍 Troubleshooting

### Common Issues

1. **Build Failures**
   - Check Python version compatibility
   - Ensure all dependencies in `requirements.txt`
   - Check build logs in Render dashboard

2. **CORS Errors**
   - Frontend and backend URLs are already configured
   - Check browser console for specific errors

3. **Database Connection**
   - Verify MongoDB connection string
   - Check network access in MongoDB Atlas

4. **API Calls Failing**
   - Verify `VITE_API_URL` environment variable
   - Check backend service is running

### Performance Tips

1. **Enable Auto-Deploy**: Render will redeploy on every push
2. **Monitor Logs**: Check service logs for errors
3. **Health Checks**: Backend has `/health` endpoint
4. **Cold Starts**: First request might be slow (free tier limitation)

## 🎉 Post-Deployment

### Testing Checklist
- [ ] Frontend loads correctly
- [ ] Search functionality works
- [ ] Robot assistant responds
- [ ] Cart operations function
- [ ] Price comparison works
- [ ] API documentation accessible (`/docs`)

### Custom Domain (Optional)
1. Go to your frontend service in Render
2. Click "Settings" → "Custom Domains"
3. Add your domain
4. Update DNS records

## 💰 Cost Breakdown
- **Render Free Tier**: $0/month
- **MongoDB Atlas**: $0/month (free tier)
- **OpenAI API**: Pay per use (optional)
- **Total**: $0/month

## 🏆 Hackathon Ready!

Your application is now:
- ✅ **Single platform** deployment
- ✅ **Completely free**
- ✅ **Production ready**
- ✅ **Scalable** (can upgrade if needed)
- ✅ **Custom domain** ready

## 📞 Support

- **Render Documentation**: https://render.com/docs
- **Render Community**: https://community.render.com
- **MongoDB Atlas**: https://docs.atlas.mongodb.com

## 🚀 Quick Commands

```bash
# Check deployment status
curl https://smartshop-backend.onrender.com/health

# Test frontend
curl https://smartshop-frontend.onrender.com

# View API docs
open https://smartshop-backend.onrender.com/docs
```

**Your SmartShop application is now live and ready for your hackathon demo!** 🎉 