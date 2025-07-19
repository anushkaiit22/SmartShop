#!/bin/bash

# SmartShop Deployment Script
# This script prepares and deploys the SmartShop application

set -e  # Exit on any error

echo "🚀 SmartShop Deployment Script"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "main.py" ] || [ ! -f "requirements.txt" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

print_status "Checking prerequisites..."

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
if [[ "$python_version" < "3.8" ]]; then
    print_error "Python 3.8 or higher is required. Found: $python_version"
    exit 1
fi
print_success "Python version: $python_version"

# Check Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed"
    exit 1
fi
print_success "Node.js version: $(node --version)"

# Check npm
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed"
    exit 1
fi
print_success "npm version: $(npm --version)"

print_status "Installing Python dependencies..."
pip install -r requirements.txt
print_success "Python dependencies installed"

print_status "Installing frontend dependencies..."
cd frontend
npm ci --only=production
print_success "Frontend dependencies installed"

print_status "Building frontend..."
npm run build
print_success "Frontend built successfully"
cd ..

print_status "Running tests..."
python test_local_deployment.py

print_status "Deployment preparation completed!"
print_success "Your application is ready for deployment to Render"
print_status "Next steps:"
echo "  1. Push your code to GitHub"
echo "  2. Go to https://dashboard.render.com"
echo "  3. Create a new Web Service from your GitHub repo"
echo "  4. Use the render.yaml file for automatic configuration"
echo "  5. Add your environment variables in the Render dashboard"
echo ""
print_warning "Make sure to set these environment variables in Render:"
echo "  - OPENAI_API_KEY"
echo "  - MONGODB_URL"
echo "  - JWT_SECRET (will be auto-generated)" 