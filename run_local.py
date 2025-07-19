#!/usr/bin/env python3
"""
Simple local startup script for SmartShop API
Handles environment setup and starts the application
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 11):
        print("❌ Error: Python 3.11 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        # import motor  # Removed for Vercel compatibility
        import pydantic
        print("✅ All required dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists and has required variables"""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found")
        print("Creating .env file from template...")
        
        # Copy from env.example if it exists
        example_file = Path("env.example")
        if example_file.exists():
            with open(example_file, 'r') as f:
                content = f.read()
            with open(env_file, 'w') as f:
                f.write(content)
            print("✅ Created .env file from template")
            print("⚠️  Please edit .env file with your API keys before running")
            return False
        else:
            print("❌ env.example not found")
            return False
    
    # Check for required environment variables
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Only OpenAI API key is required, MongoDB is optional
    required_vars = ['OPENAI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if f"{var}=" not in content or (f"{var}=" in content and "your_" in content):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing or unconfigured environment variables: {', '.join(missing_vars)}")
        print("Please edit .env file with your actual values")
        print("Note: MongoDB is optional - leave MONGODB_URL empty for memory-only mode")
        return False
    
    print("✅ Environment variables configured")
    return True

def start_application():
    """Start the FastAPI application"""
    print("\n🚀 Starting SmartShop API...")
    print("📍 API will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔄 Auto-reload enabled for development")
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        # Start the application using uvicorn
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

def main():
    """Main startup function"""
    print("🔍 SmartShop API - Local Setup Check")
    print("=" * 40)
    
    # Check Python version
    check_python_version()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment file
    if not check_env_file():
        print("\n⚠️  Please configure your .env file and run again")
        sys.exit(1)
    
    # Start the application
    start_application()

if __name__ == "__main__":
    main() 