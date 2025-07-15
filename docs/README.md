# SmartShop - Unified Shopping Assistant

A unified shopping assistant that compares prices across e-commerce and instant delivery platforms using AI-powered search and natural language processing.

## Features

- **Multi-platform Price Comparison**: Compare prices across Amazon, Flipkart, Blinkit, Zepto, Meesho, and Nykaa
- **Natural Language Search**: Search products using conversational queries
- **AI-Powered Query Parsing**: Intelligent product search using OpenAI GPT
- **Real-time Price Tracking**: Get live prices from multiple platforms
- **Shopping Cart Management**: Save and manage your shopping lists
- **Location-based Results**: Get results relevant to your location

## Quick Start (Local Setup)

For detailed setup instructions, see [SETUP_LOCAL.md](SETUP_LOCAL.md).

### Prerequisites

- Python 3.11+
- OpenAI API Key (required for AI features)
- MongoDB (optional - for persistent cart storage)
- Redis (optional, for caching)

### Quick Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp env.example .env
   # Edit .env with your API keys and database URLs
   ```

3. **Start the application**:
   ```bash
   # Using Python directly
   python run_local.py
   
   # Or use the startup scripts:
   # Windows: start.bat
   # Unix/Linux/macOS: ./start.sh
   ```

4. **Access the API**:
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

For detailed setup instructions, troubleshooting, and development workflow, see [SETUP_LOCAL.md](SETUP_LOCAL.md).

## API Endpoints

### Search & Comparison
- `GET /api/v1/search` - Search products across platforms
- `GET /api/v1/query` - Natural language product search
- `GET /api/v1/compare/{product_id}` - Compare prices for a specific product

### Shopping Cart
- `GET /api/v1/cart` - Get user's shopping cart
- `POST /api/v1/cart` - Add item to cart
- `PUT /api/v1/cart/{item_id}` - Update cart item
- `DELETE /api/v1/cart/{item_id}` - Remove item from cart

## Development

### Running Tests
```bash
python test_basic.py
```

### Project Structure
```
app/
├── api/v1/           # API endpoints
├── core/             # Configuration and settings
├── database/         # Database connections
├── models/           # Data models
└── services/         # Business logic
    ├── cart/         # Shopping cart services
    ├── nlp/          # Natural language processing
    ├── scrapers/     # Web scrapers for e-commerce sites
    └── search_service.py
```

## Configuration

The application uses environment variables for configuration. Key settings include:

- **MONGODB_URL**: MongoDB connection string
- **OPENAI_API_KEY**: OpenAI API key for AI features
- **REDIS_URL**: Redis connection for caching (optional)
- **JWT_SECRET**: Secret key for JWT tokens
- **CORS_ORIGINS**: Allowed origins for CORS

## Supported Platforms

- **Amazon**: General e-commerce
- **Flipkart**: General e-commerce  
- **Blinkit**: Instant delivery
- **Zepto**: Instant delivery
- **Meesho**: Social commerce
- **Nykaa**: Beauty and personal care

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License. 