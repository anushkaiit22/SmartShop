#!/usr/bin/env python3
"""
Deployment script for CORS fixes
"""
import os
import subprocess
import sys

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("🚀 Deploying CORS fixes to Vercel...")
    
    # Check if vercel CLI is installed
    if not run_command("vercel --version", "Checking Vercel CLI"):
        print("❌ Vercel CLI not found. Please install it first:")
        print("npm install -g vercel")
        return False
    
    # Deploy to Vercel
    if run_command("vercel --prod", "Deploying to Vercel production"):
        print("\n🎉 Deployment completed successfully!")
        print("\n📋 Next steps:")
        print("1. Wait a few minutes for the deployment to propagate")
        print("2. Test the CORS configuration using: python test_cors.py")
        print("3. Check your frontend application")
        return True
    else:
        print("\n❌ Deployment failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 