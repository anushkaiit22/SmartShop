#!/bin/bash

# Vercel Deployment Script for SmartShop
# This script helps deploy both backend and frontend to Vercel

set -e

echo "🚀 Starting Vercel Deployment for SmartShop"
echo "=========================================="

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Check if user is logged in
if ! vercel whoami &> /dev/null; then
    echo "🔐 Please login to Vercel..."
    vercel login
fi

echo ""
echo "📦 Deploying Backend API..."
echo "=========================="

# Deploy backend
echo "Deploying from root directory..."
vercel --prod

echo ""
echo "🎨 Deploying Frontend..."
echo "======================="

# Deploy frontend
cd frontend
echo "Deploying from frontend directory..."
vercel --prod

echo ""
echo "✅ Deployment Complete!"
echo "======================"
echo ""
echo "📋 Next Steps:"
echo "1. Set environment variables in Vercel dashboard"
echo "2. Update CORS origins with your frontend URL"
echo "3. Test your deployment"
echo ""
echo "📚 See VERCEL_DEPLOYMENT.md for detailed instructions" 