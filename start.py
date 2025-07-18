#!/usr/bin/env python3
"""
Quick start script for SmartShop Backend
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import pydantic
        import motor
        import redis
        print("All required packages are installed")
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def setup_environment():
    """Setup environment file if it doesn't exist"""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if not env_file.exists() and env_example.exists():
        print("📝 Creating .env file from template...")
        with open(env_example, 'r') as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✓ .env file created. Please edit it with your configuration.")
        return False
    elif env_file.exists():
        print("✓ .env file found")
        return True
    else:
        print("❌ No environment template found")
        return False

def check_services():
    """Check if required services are running"""
    import socket
    
    services = [
        ("MongoDB", "localhost", 27017),
        ("Redis", "localhost", 6379)
    ]
    
    all_running = True
    for name, host, port in services:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"✓ {name} is running on {host}:{port}")
            else:
                print(f"❌ {name} is not running on {host}:{port}")
                all_running = False
        except Exception as e:
            print(f"❌ Could not check {name}: {e}")
            all_running = False
    
    return all_running

def start_services():
    """Provide guidance for starting services manually"""
    print("\n📋 Services Setup Required")
    print("Please start the following services manually:")
    print("1. MongoDB: mongod (or use MongoDB Atlas)")
    print("2. Redis: redis-server (optional, for caching)")
    print("\nFor detailed setup instructions, see SETUP_LOCAL.md")
    return False

def run_tests():
    """Run basic tests"""
    print("\n🧪 Running basic tests...")
    
    try:
        result = subprocess.run([sys.executable, "test_basic.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ All tests passed")
            return True
        else:
            print("❌ Some tests failed:")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def start_application():
    """Start the FastAPI application"""
    print("\n🚀 Starting SmartShop Backend...")
    
    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")

def main():
    """Main function"""
    print("SmartShop Backend - Quick Start")
    print("=" * 40)
    
    # Check Python version
    check_python_version()
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Setup environment
    if not setup_environment():
        print("\nPlease configure your .env file and run this script again.")
        return
    
    # Check if services are running
    if not check_services():
        print("\nSome services are not running.")
        start_services()
        print("\nPlease start the required services and run this script again.")
        return
    
    # Run tests
    if not run_tests():
        print("Tests failed. Please check the errors above.")
        return
    
    # Start application
    start_application()

if __name__ == "__main__":
    main() 