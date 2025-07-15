# Quick Test Guide - No MongoDB Required

This guide will help you test SmartShop functionality without setting up MongoDB or Redis.

## 🚀 Quick Start (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment (Minimal Setup)
```bash
# Copy environment template
cp env.example .env

# Edit .env file - you only need OpenAI API key
```

**Minimal `.env` file:**
```env
# Required: OpenAI API Key for AI features
OPENAI_API_KEY=sk-your-openai-api-key-here

# Optional: Leave empty for memory-only mode
MONGODB_URL=
REDIS_URL=

# JWT Secret (can be any string for testing)
JWT_SECRET=test-secret-key
```

### 3. Test Core Functionality
```bash
python test_core_functionality.py
```

This will verify that:
- ✅ All imports work
- ✅ Search service initializes
- ✅ Cart service works (in-memory mode)
- ✅ API endpoints are available
- ✅ No MongoDB required

### 4. Start the Application
```bash
python run_local.py
```

### 5. Test the API
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **API Base**: http://localhost:8000/api/v1

## 🧪 What You Can Test

### Search Functionality
```bash
# Test search endpoint
curl "http://localhost:8000/api/v1/search?query=laptop&platforms=amazon,flipkart"
```

### Cart Functionality (In-Memory)
```bash
# Create a cart
curl -X POST "http://localhost:8000/api/v1/cart" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test-session"}'

# Get cart (use the cart ID from previous response)
curl "http://localhost:8000/api/v1/cart/{cart_id}"
```

### Natural Language Search
```bash
# Test NLP query parsing
curl -X POST "http://localhost:8000/api/v1/query/parse" \
  -H "Content-Type: application/json" \
  -d '{"query": "I need a laptop under 50000 rupees"}'
```

## 📊 Available Platforms

- **Amazon** - General e-commerce
- **Flipkart** - General e-commerce  
- **Blinkit** - Quick commerce (instant delivery)

## 🔄 Memory-Only Mode

When MongoDB is not configured:
- ✅ Carts are stored in memory
- ✅ Data persists during the session
- ❌ Data is lost when server restarts
- ✅ Perfect for testing and development

## 🚨 Limitations

1. **Cart Persistence**: Carts are lost when server restarts
2. **No User Accounts**: No persistent user data
3. **Single Server**: Won't work with multiple server instances

## 🎯 Next Steps

Once you're satisfied with the functionality:

1. **Add MongoDB** for persistent cart storage
2. **Add Redis** for caching
3. **Deploy to production**

## 🆘 Troubleshooting

### OpenAI API Error
```
openai.AuthenticationError: Incorrect API key provided
```
**Solution**: Get a valid API key from https://platform.openai.com/

### Import Errors
```
ModuleNotFoundError: No module named 'fastapi'
```
**Solution**: Run `pip install -r requirements.txt`

### Port Already in Use
```
OSError: [Errno 48] Address already in use
```
**Solution**: Change port in `main.py` or kill existing process

## 📝 Test Results

After running `python test_core_functionality.py`, you should see:
```
🎉 Core functionality test completed successfully!

📝 Summary:
   - Search service: ✅ Working
   - Cart service: ✅ Working (in-memory mode)
   - Platform scrapers: ✅ Available
   - No MongoDB required: ✅ Running in memory-only mode
```

If you see this, you're ready to test the full application! 