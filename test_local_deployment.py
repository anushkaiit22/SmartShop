#!/usr/bin/env python3
"""
Local Deployment Test Script for SmartShop
Tests all components before deploying to Render
"""

import os
import sys
import subprocess
import requests
import time
import json
from pathlib import Path

class LocalDeploymentTester:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:5173"  # Vite default port
        self.backend_process = None
        self.frontend_process = None
        
    def print_status(self, message, status="INFO"):
        """Print formatted status messages"""
        colors = {
            "INFO": "\033[94m",    # Blue
            "SUCCESS": "\033[92m", # Green
            "WARNING": "\033[93m", # Yellow
            "ERROR": "\033[91m",   # Red
            "RESET": "\033[0m"     # Reset
        }
        print(f"{colors.get(status, colors['INFO'])}[{status}]{colors['RESET']} {message}")
    
    def check_dependencies(self):
        """Check if all required dependencies are installed"""
        self.print_status("Checking dependencies...")
        
        # Check Python dependencies
        try:
            import fastapi
            import uvicorn
            # import pymongo  # Removed for Vercel compatibility
            import requests
            import bs4  # beautifulsoup4 is imported as bs4
            self.print_status("✅ Python dependencies found", "SUCCESS")
        except ImportError as e:
            self.print_status(f"❌ Missing Python dependency: {e}", "ERROR")
            return False
        
        # Check Node.js and npm
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                self.print_status(f"✅ Node.js found: {result.stdout.strip()}", "SUCCESS")
            else:
                self.print_status("❌ Node.js not found", "ERROR")
                return False
        except FileNotFoundError:
            self.print_status("❌ Node.js not found", "ERROR")
            return False
        
        try:
            result = subprocess.run(['npm', '--version'], capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                self.print_status(f"✅ npm found: {result.stdout.strip()}", "SUCCESS")
            else:
                self.print_status("❌ npm not found", "ERROR")
                return False
        except FileNotFoundError:
            self.print_status("❌ npm not found", "ERROR")
            return False
        
        return True
    
    def check_files(self):
        """Check if all required files exist"""
        self.print_status("Checking required files...")
        
        required_files = [
            "main.py",
            "requirements.txt",
            "render.yaml",
            "frontend/package.json",
            "frontend/vite.config.js",
            "app/core/config.py",
            ".env"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
            else:
                self.print_status(f"✅ {file_path}", "SUCCESS")
        
        if missing_files:
            self.print_status(f"❌ Missing files: {missing_files}", "ERROR")
            return False
        
        return True
    
    def install_frontend_dependencies(self):
        """Install frontend dependencies"""
        self.print_status("Installing frontend dependencies...")
        
        try:
            # Get absolute path to frontend directory
            frontend_path = Path("frontend").absolute()
            if not frontend_path.exists():
                self.print_status(f"❌ Frontend directory not found: {frontend_path}", "ERROR")
                return False
                
            # Change to frontend directory
            original_dir = os.getcwd()
            os.chdir(frontend_path)
            
            # Run npm install
            result = subprocess.run(['npm', 'install'], capture_output=True, text=True, shell=True)
            
            # Return to original directory
            os.chdir(original_dir)
            
            if result.returncode == 0:
                self.print_status("✅ Frontend dependencies installed", "SUCCESS")
                return True
            else:
                self.print_status(f"❌ Frontend installation failed: {result.stderr}", "ERROR")
                return False
        except Exception as e:
            self.print_status(f"❌ Frontend installation error: {e}", "ERROR")
            return False
    
    def start_backend(self):
        """Start the backend server"""
        self.print_status("Starting backend server...")
        
        try:
            # Set environment variables for testing
            env = os.environ.copy()
            env['DEBUG'] = 'true'
            env['PORT'] = '8000'
            
            # Check if main.py exists
            if not Path("main.py").exists():
                self.print_status("❌ main.py not found", "ERROR")
                return False
            
            self.backend_process = subprocess.Popen(
                [sys.executable, 'main.py'],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True
            )
            
            # Wait for backend to start
            time.sleep(8)  # Give more time for startup
            
            # Test if backend is running
            try:
                response = requests.get(f"{self.backend_url}/health", timeout=10)
                if response.status_code == 200:
                    self.print_status("✅ Backend server started successfully", "SUCCESS")
                    return True
                else:
                    self.print_status(f"❌ Backend health check failed: {response.status_code}", "ERROR")
                    return False
            except requests.exceptions.RequestException as e:
                self.print_status(f"❌ Backend not responding: {e}", "ERROR")
                return False
                
        except Exception as e:
            self.print_status(f"❌ Failed to start backend: {e}", "ERROR")
            return False
    
    def start_frontend(self):
        """Start the frontend development server"""
        self.print_status("Starting frontend server...")
        
        try:
            # Get absolute path to frontend directory
            frontend_path = Path("frontend").absolute()
            if not frontend_path.exists():
                self.print_status(f"❌ Frontend directory not found: {frontend_path}", "ERROR")
                return False
                
            # Change to frontend directory
            original_dir = os.getcwd()
            os.chdir(frontend_path)
            
            # Start frontend server
            self.frontend_process = subprocess.Popen(
                ['npm', 'run', 'dev'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                env=os.environ.copy()
            )
            
            # Return to original directory
            os.chdir(original_dir)
            
            # Wait for frontend to start
            time.sleep(20)  # Give more time for Vite to start
            
            # Test if frontend is running
            try:
                response = requests.get(self.frontend_url, timeout=15)
                if response.status_code == 200:
                    self.print_status("✅ Frontend server started successfully", "SUCCESS")
                    return True
                else:
                    self.print_status(f"❌ Frontend not responding: {response.status_code}", "ERROR")
                    return False
            except requests.exceptions.RequestException as e:
                self.print_status(f"❌ Frontend not accessible: {e}", "ERROR")
                # Try to get more info about the frontend process
                if self.frontend_process:
                    try:
                        stdout, stderr = self.frontend_process.communicate(timeout=1)
                        if stderr:
                            self.print_status(f"Frontend stderr: {stderr.decode()[:200]}", "WARNING")
                    except:
                        pass
                return False
                
        except Exception as e:
            self.print_status(f"❌ Failed to start frontend: {e}", "ERROR")
            return False
    
    def test_backend_endpoints(self):
        """Test backend API endpoints"""
        self.print_status("Testing backend endpoints...")
        
        endpoints_to_test = [
            ("/", "Root endpoint"),
            ("/health", "Health check"),
            ("/docs", "API documentation"),
            ("/api/v1/search/?q=test&limit=5", "Search endpoint")
        ]
        
        failed_endpoints = []
        for endpoint, description in endpoints_to_test:
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=10)
                if response.status_code in [200, 404]:  # 404 is OK for search with no results
                    self.print_status(f"✅ {description}: {response.status_code}", "SUCCESS")
                else:
                    self.print_status(f"⚠️ {description}: {response.status_code}", "WARNING")
                    failed_endpoints.append(description)
            except requests.exceptions.RequestException as e:
                self.print_status(f"❌ {description}: {e}", "ERROR")
                failed_endpoints.append(description)
        
        return len(failed_endpoints) == 0
    
    def test_frontend_functionality(self):
        """Test frontend functionality"""
        self.print_status("Testing frontend functionality...")
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            if response.status_code == 200:
                if "SmartShop" in response.text or "React" in response.text:
                    self.print_status("✅ Frontend loads correctly", "SUCCESS")
                    return True
                else:
                    self.print_status("⚠️ Frontend content seems unusual", "WARNING")
                    return False
            else:
                self.print_status(f"❌ Frontend not accessible: {response.status_code}", "ERROR")
                return False
        except requests.exceptions.RequestException as e:
            self.print_status(f"❌ Frontend test failed: {e}", "ERROR")
            return False
    
    def check_environment_variables(self):
        """Check environment variables"""
        self.print_status("Checking environment variables...")
        
        # Load .env file if it exists
        env_file = Path(".env")
        if env_file.exists():
            self.print_status("✅ .env file found", "SUCCESS")
            
            # Check for required variables
            with open(env_file, 'r') as f:
                content = f.read()
                
            required_vars = ['OPENAI_API_KEY', 'MONGODB_URL', 'JWT_SECRET']
            missing_vars = []
            for var in required_vars:
                if var in content:
                    self.print_status(f"✅ {var} found in .env", "SUCCESS")
                else:
                    self.print_status(f"⚠️ {var} not found in .env", "WARNING")
                    missing_vars.append(var)
            
            return len(missing_vars) == 0
        else:
            self.print_status("⚠️ .env file not found", "WARNING")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        self.print_status("🚀 Starting Local Deployment Test", "INFO")
        self.print_status("=" * 50, "INFO")
        
        tests = [
            ("Dependencies", self.check_dependencies),
            ("Required Files", self.check_files),
            ("Environment Variables", self.check_environment_variables),
            ("Frontend Dependencies", self.install_frontend_dependencies),
            ("Backend Server", self.start_backend),
            ("Frontend Server", self.start_frontend),
            ("Backend Endpoints", self.test_backend_endpoints),
            ("Frontend Functionality", self.test_frontend_functionality)
        ]
        
        results = []
        for test_name, test_func in tests:
            self.print_status(f"\n--- Testing {test_name} ---", "INFO")
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                self.print_status(f"❌ {test_name} test failed with exception: {e}", "ERROR")
                results.append((test_name, False))
        
        # Summary
        self.print_status("\n" + "=" * 50, "INFO")
        self.print_status("📊 TEST SUMMARY", "INFO")
        self.print_status("=" * 50, "INFO")
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            self.print_status(f"{status} - {test_name}", "SUCCESS" if result else "ERROR")
        
        self.print_status(f"\nOverall: {passed}/{total} tests passed", "SUCCESS" if passed == total else "WARNING")
        
        if passed == total:
            self.print_status("🎉 All tests passed! Ready for deployment!", "SUCCESS")
        else:
            self.print_status("⚠️ Some tests failed. Please fix issues before deploying.", "WARNING")
        
        return passed == total
    
    def cleanup(self):
        """Clean up running processes"""
        self.print_status("Cleaning up...")
        
        if self.backend_process:
            self.backend_process.terminate()
            self.backend_process.wait()
            self.print_status("✅ Backend process terminated", "SUCCESS")
        
        if self.frontend_process:
            self.frontend_process.terminate()
            self.frontend_process.wait()
            self.print_status("✅ Frontend process terminated", "SUCCESS")

def main():
    tester = LocalDeploymentTester()
    
    try:
        success = tester.run_all_tests()
        
        if success:
            print("\n" + "=" * 60)
            print("🎉 LOCAL DEPLOYMENT TEST COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print("✅ Your application is ready for deployment to Render!")
            print("📖 Next steps:")
            print("   1. Push your code to GitHub")
            print("   2. Go to https://dashboard.render.com")
            print("   3. Deploy using the Blueprint option")
            print("   4. Add environment variables in Render dashboard")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("⚠️ LOCAL DEPLOYMENT TEST FAILED!")
            print("=" * 60)
            print("❌ Please fix the issues above before deploying.")
            print("🔧 Common fixes:")
            print("   - Install missing dependencies")
            print("   - Create .env file with required variables")
            print("   - Check file permissions")
            print("   - Ensure ports 8000 and 3000 are available")
            print("=" * 60)
    
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    finally:
        tester.cleanup()

if __name__ == "__main__":
    main() 