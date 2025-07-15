# Local Development Setup Guide

This guide will help you set up SmartShop API for local development without Docker.

## Prerequisites

### 1. Python 3.11+
Make sure you have Python 3.11 or higher installed:
```bash
python --version
```

### 2. MongoDB
You have two options for MongoDB:

#### Option A: Local MongoDB Installation
- **Windows**: Download and install from [MongoDB Download Center](https://www.mongodb.com/try/download/community)
- **macOS**: `brew install mongodb-community`
- **Linux**: Follow [MongoDB Installation Guide](https://docs.mongodb.com/manual/installation/)

#### Option B: MongoDB Atlas (Cloud - Recommended)
1. Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create a free account
3. Create a new cluster
4. Get your connection string (looks like: `mongodb+srv://username:password@cluster.mongodb.net/`)

### 3. OpenAI API Key (Required)
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create an account and get your API key
3. You'll need this for AI-powered search features

### 4. Redis (Optional)
Redis is used for caching. If you don't have Redis, the app will work without it:
- **Windows**: Download from [Redis for Windows](https://github.com/microsoftarchive/redis/releases)
- **macOS**: `brew install redis`
- **Linux**: `sudo apt-get install redis-server`

## Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy the example environment file
cp env.example .env

# Edit the .env file with your settings
```

### 3. Update .env File
Edit the `.env` file with your actual values:

```env
# Required: Your OpenAI API key
OPENAI_API_KEY=sk-your-actual-openai-api-key-here

# Database: Use your MongoDB connection string
MONGODB_URL=mongodb://localhost:27017
# OR for MongoDB Atlas:
# MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/

# Database name
MONGODB_DB_NAME=smartshop

# Optional: Redis for caching (leave empty if not using Redis)
REDIS_URL=redis://localhost:6379
# OR leave empty:
# REDIS_URL=

# JWT Secret (change this in production)
JWT_SECRET=your-super-secret-jwt-key-change-in-production
```

### 4. Start the Application

#### Option A: Using the startup script (Recommended)
```bash
python run_local.py
```

#### Option B: Direct start
```bash
python main.py
```

#### Option C: Using uvicorn directly
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Verify Installation
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Testing the Setup

### 1. Basic Health Check
Visit http://localhost:8000/health - you should see:
```json
{
  "status": "healthy",
  "service": "smartshop-backend"
}
```

### 2. API Documentation
Visit http://localhost:8000/docs to see the interactive API documentation.

### 3. Test Search Endpoint
Try a simple search:
```bash
curl "http://localhost:8000/api/v1/search?query=laptop&platform=amazon"
```

## Troubleshooting

### Common Issues

#### 1. MongoDB Connection Error
```
Failed to connect to MongoDB: [Errno 61] Connection refused
```
**Solution**: 
- Make sure MongoDB is running locally: `mongod`
- Or check your MongoDB Atlas connection string

#### 2. OpenAI API Error
```
openai.AuthenticationError: Incorrect API key provided
```
**Solution**: 
- Check your OpenAI API key in the `.env` file
- Make sure you have credits in your OpenAI account

#### 3. Missing Dependencies
```
ModuleNotFoundError: No module named 'fastapi'
```
**Solution**: 
```bash
pip install -r requirements.txt
```

#### 4. Port Already in Use
```
OSError: [Errno 48] Address already in use
```
**Solution**: 
- Change the port in `main.py` or use a different port:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### Getting Help

1. Check the logs in your terminal for error messages
2. Verify all environment variables are set correctly
3. Make sure all services (MongoDB, Redis) are running
4. Check the API documentation at http://localhost:8000/docs

## Development Workflow

1. **Start the server**: `python run_local.py`
2. **Make changes** to your code
3. **Server auto-reloads** when you save files
4. **Test endpoints** using the docs or curl
5. **Stop server**: Press `Ctrl+C`

## Next Steps

Once your local setup is working:

1. Explore the API endpoints in the documentation
2. Try the search and cart features
3. Check out the project structure in `PROJECT_STRUCTURE.md`
4. Run tests: `python test_basic.py`
5. Start building new features! 