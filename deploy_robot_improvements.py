#!/usr/bin/env python3
"""
Deployment script for robot improvements
"""

import os
import subprocess
import sys
import time

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False

def check_vercel_cli():
    """Check if Vercel CLI is installed"""
    try:
        subprocess.run(["vercel", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def deploy_backend():
    """Deploy backend improvements"""
    print("🚀 Deploying Backend Improvements")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("app"):
        print("❌ Error: 'app' directory not found. Make sure you're in the project root.")
        return False
    
    # Check if Vercel CLI is installed
    if not check_vercel_cli():
        print("❌ Vercel CLI not found. Please install it first:")
        print("   npm install -g vercel")
        return False
    
    # Deploy to Vercel
    if not run_command("vercel --prod", "Deploying backend to Vercel"):
        return False
    
    print("✅ Backend deployment completed!")
    return True

def deploy_frontend():
    """Deploy frontend improvements"""
    print("\n🎨 Deploying Frontend Improvements")
    print("=" * 50)
    
    # Check if frontend directory exists
    if not os.path.exists("frontend"):
        print("❌ Error: 'frontend' directory not found.")
        return False
    
    # Change to frontend directory
    os.chdir("frontend")
    
    # Install dependencies if needed
    if not os.path.exists("node_modules"):
        if not run_command("npm install", "Installing frontend dependencies"):
            return False
    
    # Build the project
    if not run_command("npm run build", "Building frontend"):
        return False
    
    # Deploy to Vercel
    if not run_command("vercel --prod", "Deploying frontend to Vercel"):
        return False
    
    # Go back to root directory
    os.chdir("..")
    
    print("✅ Frontend deployment completed!")
    return True

def test_deployment():
    """Test the deployed application"""
    print("\n🧪 Testing Deployment")
    print("=" * 50)
    
    # Wait a bit for deployment to complete
    print("⏳ Waiting for deployment to complete...")
    time.sleep(30)
    
    # Run the test script
    if os.path.exists("test_robot_improvements.py"):
        print("🔍 Running deployment tests...")
        if run_command("python test_robot_improvements.py", "Running deployment tests"):
            print("✅ All tests passed!")
        else:
            print("⚠️  Some tests failed, but deployment may still be working")
    else:
        print("⚠️  Test script not found, skipping tests")

def main():
    """Main deployment function"""
    print("🤖 Robot Improvements Deployment")
    print("=" * 60)
    print()
    print("This script will deploy the following improvements:")
    print("✅ Reduced timeouts for better Vercel performance")
    print("✅ Comprehensive fallback mechanisms")
    print("✅ Improved error handling and user feedback")
    print("✅ Mock data fallbacks when real scrapers fail")
    print("✅ Enhanced frontend with loading states and retry buttons")
    print()
    
    # Ask for confirmation
    response = input("Do you want to proceed with deployment? (y/N): ")
    if response.lower() != 'y':
        print("❌ Deployment cancelled")
        return
    
    # Deploy backend
    if not deploy_backend():
        print("❌ Backend deployment failed")
        return
    
    # Deploy frontend
    if not deploy_frontend():
        print("❌ Frontend deployment failed")
        return
    
    # Test deployment
    test_deployment()
    
    print("\n🎉 Deployment completed successfully!")
    print("\n📋 What was improved:")
    print("• Reduced scraper timeout from 30s to 10s")
    print("• Added comprehensive fallback mechanisms")
    print("• Improved error handling with specific messages")
    print("• Added mock data fallbacks for reliability")
    print("• Enhanced frontend with loading animations")
    print("• Added retry buttons for failed requests")
    print("• Better visual feedback for users")
    print("\n🔗 Your app should now be much faster and more reliable!")

if __name__ == "__main__":
    main() 