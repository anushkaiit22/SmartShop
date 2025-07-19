@echo off
REM Vercel Deployment Script for SmartShop (Windows)
REM This script helps deploy both backend and frontend to Vercel

echo 🚀 Starting Vercel Deployment for SmartShop
echo ==========================================

REM Check if Vercel CLI is installed
vercel --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Vercel CLI not found. Installing...
    npm install -g vercel
)

REM Check if user is logged in
vercel whoami >nul 2>&1
if errorlevel 1 (
    echo 🔐 Please login to Vercel...
    vercel login
)

echo.
echo 📦 Deploying Backend API...
echo ==========================

REM Deploy backend
echo Deploying from root directory...
vercel --prod

echo.
echo 🎨 Deploying Frontend...
echo =======================

REM Deploy frontend
cd frontend
echo Deploying from frontend directory...
vercel --prod

echo.
echo ✅ Deployment Complete!
echo ======================
echo.
echo 📋 Next Steps:
echo 1. Set environment variables in Vercel dashboard
echo 2. Update CORS origins with your frontend URL
echo 3. Test your deployment
echo.
echo 📚 See VERCEL_DEPLOYMENT.md for detailed instructions

pause 