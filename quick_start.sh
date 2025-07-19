#!/bin/bash

echo "🚀 SmartShop Quick Start - Complete Deployment"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local message=$1
    local color=$2
    echo -e "${color}${message}${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is available
port_available() {
    ! lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1
}

print_status "📋 Checking Prerequisites..." "$BLUE"

# Check Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    print_status "✅ Python found: $PYTHON_VERSION" "$GREEN"
else
    print_status "❌ Python 3 not found. Please install Python 3.11+" "$RED"
    exit 1
fi

# Check Node.js
if command_exists node; then
    NODE_VERSION=$(node --version)
    print_status "✅ Node.js found: $NODE_VERSION" "$GREEN"
else
    print_status "❌ Node.js not found. Please install Node.js 18+" "$RED"
    exit 1
fi

# Check npm
if command_exists npm; then
    NPM_VERSION=$(npm --version)
    print_status "✅ npm found: $NPM_VERSION" "$GREEN"
else
    print_status "❌ npm not found. Please install npm" "$RED"
    exit 1
fi

# Check Git
if command_exists git; then
    print_status "✅ Git found" "$GREEN"
else
    print_status "❌ Git not found. Please install Git" "$RED"
    exit 1
fi

# Check ports
if port_available 8000; then
    print_status "✅ Port 8000 available" "$GREEN"
else
    print_status "⚠️ Port 8000 is in use. Please free it up." "$YELLOW"
fi

if port_available 3000; then
    print_status "✅ Port 3000 available" "$GREEN"
else
    print_status "⚠️ Port 3000 is in use. Please free it up." "$YELLOW"
fi

echo ""
print_status "🔧 Step 1: Installing Dependencies..." "$BLUE"

# Install Python dependencies
print_status "Installing Python dependencies..." "$BLUE"
if pip3 install -r requirements.txt; then
    print_status "✅ Python dependencies installed" "$GREEN"
else
    print_status "❌ Failed to install Python dependencies" "$RED"
    exit 1
fi

# Install frontend dependencies
print_status "Installing frontend dependencies..." "$BLUE"
cd frontend
if npm install; then
    print_status "✅ Frontend dependencies installed" "$GREEN"
else
    print_status "❌ Failed to install frontend dependencies" "$RED"
    exit 1
fi
cd ..

echo ""
print_status "📝 Step 2: Setting up Environment..." "$BLUE"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating .env file..." "$BLUE"
    cat > .env << EOF
# Backend Environment Variables
OPENAI_API_KEY=your_openai_api_key_here
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/smartshop
JWT_SECRET=your_super_secure_jwt_secret_here
REDIS_URL=your_redis_url_here
DEBUG=true

# Frontend Environment Variables
VITE_API_URL=http://localhost:8000
EOF
    print_status "✅ .env file created" "$GREEN"
    print_status "⚠️ Please update .env with your actual API keys" "$YELLOW"
else
    print_status "✅ .env file already exists" "$GREEN"
fi

echo ""
print_status "🧪 Step 3: Running Local Tests..." "$BLUE"

# Run local deployment test
if [ -f "test_local_deployment.py" ]; then
    print_status "Running comprehensive local test..." "$BLUE"
    if python3 test_local_deployment.py; then
        print_status "✅ Local tests passed!" "$GREEN"
    else
        print_status "❌ Local tests failed. Please check the errors above." "$RED"
        print_status "You can still proceed with deployment, but issues may occur." "$YELLOW"
        read -p "Continue with deployment? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    print_status "⚠️ test_local_deployment.py not found. Skipping automated tests." "$YELLOW"
fi

echo ""
print_status "📦 Step 4: Preparing for Deployment..." "$BLUE"

# Check if git is initialized
if [ ! -d ".git" ]; then
    print_status "Initializing Git repository..." "$BLUE"
    git init
    git add .
    git commit -m "Initial commit - SmartShop hackathon project"
    print_status "✅ Git repository initialized" "$GREEN"
else
    print_status "✅ Git repository already exists" "$GREEN"
fi

# Check if remote origin exists
if ! git remote get-url origin > /dev/null 2>&1; then
    print_status "⚠️ No remote origin found." "$YELLOW"
    echo ""
    print_status "To complete deployment, you need to:" "$BLUE"
    echo "1. Create a GitHub repository at https://github.com"
    echo "2. Add it as remote origin:"
    echo "   git remote add origin https://github.com/YOUR_USERNAME/smartshop-hackathon.git"
    echo "3. Push your code:"
    echo "   git push -u origin main"
    echo ""
    print_status "After pushing to GitHub, deploy to Render:" "$BLUE"
    echo "1. Go to https://dashboard.render.com"
    echo "2. Click 'New +' → 'Blueprint'"
    echo "3. Connect your GitHub repository"
    echo "4. Click 'Apply' to deploy"
    echo ""
    print_status "📖 See COMPLETE_DEPLOYMENT_GUIDE.md for detailed instructions" "$BLUE"
else
    print_status "✅ Remote origin configured" "$GREEN"
    print_status "Pushing to GitHub..." "$BLUE"
    if git push origin main; then
        print_status "✅ Code pushed to GitHub" "$GREEN"
        echo ""
        print_status "🎉 Ready for Render deployment!" "$GREEN"
        echo ""
        print_status "Next steps:" "$BLUE"
        echo "1. Go to https://dashboard.render.com"
        echo "2. Click 'New +' → 'Blueprint'"
        echo "3. Select your repository"
        echo "4. Click 'Apply' to deploy"
        echo "5. Configure environment variables in Render dashboard"
        echo ""
        print_status "📖 See COMPLETE_DEPLOYMENT_GUIDE.md for detailed instructions" "$BLUE"
    else
        print_status "❌ Failed to push to GitHub" "$RED"
        print_status "Please check your GitHub repository and try again." "$YELLOW"
    fi
fi

echo ""
print_status "🎯 Quick Test Commands:" "$BLUE"
echo "Backend:  python3 main.py"
echo "Frontend: cd frontend && npm run dev"
echo "Test:     python3 test_local_deployment.py"
echo ""
print_status "🌐 Your URLs will be:" "$BLUE"
echo "Frontend: https://smartshop-frontend.onrender.com"
echo "Backend:  https://smartshop-backend.onrender.com"
echo ""
print_status "🏆 Good luck with your hackathon!" "$GREEN" 