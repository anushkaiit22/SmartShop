#!/usr/bin/env python3
"""
Simple deployment script for CORS fix
"""
import subprocess
import sys
import time

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("🚀 Deploying simplified CORS fix to Vercel...")
    print("\n📋 Changes made:")
    print("- Simplified CORS middleware configuration")
    print("- Removed complex custom middleware")
    print("- Added wildcard support for Vercel domains")
    print("- Streamlined robot endpoint responses")
    
    # Check if vercel CLI is installed
    if not run_command("vercel --version", "Checking Vercel CLI"):
        print("❌ Vercel CLI not found. Please install it first:")
        print("npm install -g vercel")
        return False
    
    # Deploy to Vercel
    if run_command("vercel --prod", "Deploying to Vercel production"):
        print("\n🎉 Deployment completed successfully!")
        print("\n⏳ Waiting 2 minutes for deployment to propagate...")
        time.sleep(120)
        
        print("\n🧪 Testing CORS configuration...")
        if run_command("python test_cors.py", "Running CORS tests"):
            print("\n✅ CORS fix appears to be working!")
        else:
            print("\n⚠️  CORS tests failed. Please check manually.")
        
        print("\n📋 Next steps:")
        print("1. Test your frontend application")
        print("2. Check browser console for any remaining CORS errors")
        print("3. If issues persist, wait a few more minutes and test again")
        return True
    else:
        print("\n❌ Deployment failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 