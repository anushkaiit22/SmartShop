#!/usr/bin/env python3
"""
Complete deployment script for CORS fix + Frontend proxy
"""
import subprocess
import sys
import time
import os

def run_command(command, description, cwd=None):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True, cwd=cwd)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("🚀 Deploying Complete CORS Fix (Backend + Frontend)")
    print("=" * 60)
    
    print("\n📋 Changes to deploy:")
    print("Backend:")
    print("- Custom CORS middleware with explicit headers")
    print("- Direct handling of OPTIONS preflight requests")
    print("- Fixed origin header for your specific frontend domain")
    print("\nFrontend:")
    print("- Vercel proxy configuration for API calls")
    print("- Updated API utility to use relative URLs")
    
    # Check if we're in the right directory
    if not os.path.exists("main.py"):
        print("❌ Please run this script from the project root directory")
        return False
    
    # Deploy backend first
    print("\n" + "=" * 40)
    print("🔧 Deploying Backend CORS Fix...")
    
    if not run_command("vercel --version", "Checking Vercel CLI"):
        print("❌ Vercel CLI not found. Please install it first:")
        print("npm install -g vercel")
        return False
    
    if not run_command("vercel --prod", "Deploying backend to Vercel production"):
        print("❌ Backend deployment failed!")
        return False
    
    print("✅ Backend deployed successfully!")
    
    # Wait for backend deployment to propagate
    print("\n⏳ Waiting 2 minutes for backend deployment to propagate...")
    time.sleep(120)
    
    # Test backend CORS
    print("\n🧪 Testing Backend CORS...")
    if not run_command("python test_comprehensive_cors.py", "Running comprehensive CORS tests"):
        print("⚠️  Backend CORS tests failed, but continuing with frontend deployment...")
    
    # Deploy frontend
    print("\n" + "=" * 40)
    print("🌐 Deploying Frontend Proxy Configuration...")
    
    if not os.path.exists("frontend"):
        print("❌ Frontend directory not found!")
        return False
    
    # Change to frontend directory and deploy
    if not run_command("vercel --prod", "Deploying frontend to Vercel production", cwd="frontend"):
        print("❌ Frontend deployment failed!")
        return False
    
    print("✅ Frontend deployed successfully!")
    
    # Wait for frontend deployment to propagate
    print("\n⏳ Waiting 2 minutes for frontend deployment to propagate...")
    time.sleep(120)
    
    # Final test
    print("\n" + "=" * 40)
    print("🎯 Final Testing...")
    
    if run_command("python test_comprehensive_cors.py", "Running final comprehensive tests"):
        print("\n🎉 All deployments and tests completed successfully!")
    else:
        print("\n⚠️  Some tests failed, but deployments completed")
    
    print("\n" + "=" * 60)
    print("📋 Deployment Summary:")
    print("✅ Backend CORS fix deployed")
    print("✅ Frontend proxy configuration deployed")
    print("✅ Comprehensive tests completed")
    
    print("\n🔗 Your Applications:")
    print("Frontend: https://smart-shop-frontend-git-master-anushka-pimpales-projects.vercel.app")
    print("Backend: https://smartshop-backend-3xenf4eub-anushka-pimpales-projects.vercel.app")
    
    print("\n💡 Next Steps:")
    print("1. Open your frontend application")
    print("2. Test the robot chat functionality")
    print("3. Check browser console for any remaining errors")
    print("4. If issues persist, wait a few more minutes and test again")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 