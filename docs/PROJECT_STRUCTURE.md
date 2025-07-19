# SmartShop Backend - Project Structure

## 📁 Directory Structure

```
smartshop_backend/
├── app/                          # Main application package
│   ├── __init__.py
│   ├── api/                      # API routes and endpoints
│   │   ├── __init__.py
│   │   └── v1/                   # API version 1
│   │       ├── __init__.py
│   │       ├── api.py            # Main API router
│   │       └── endpoints/        # API endpoint modules
│   │           ├── __init__.py
│   │           ├── search.py     # Product search endpoints
│   │           ├── cart.py       # Cart management endpoints
│   │           └── query.py      # NLP query endpoints
│   ├── core/                     # Core configuration and utilities
│   │   ├── __init__.py
│   │   └── config.py             # Application settings
│   ├── database/                 # Database models and connections
│   │   ├── __init__.py
│   │   └── mongodb.py            # MongoDB connection management
│   ├── models/                   # Pydantic data models
│   │   ├── __init__.py
│   │   ├── product.py            # Product-related models
│   │   └── cart.py               # Cart-related models
│   ├── services/                 # Business logic services
│   │   ├── __init__.py
│   │   ├── search_service.py     # Main search coordination service
│   │   ├── nlp/                  # Natural Language Processing
│   │   │   ├── __init__.py
│   │   │   └── query_parser.py   # NLP query parsing service
│   │   ├── scrapers/             # Web scraping services
│   │   │   ├── __init__.py
│   │   │   ├── base_scraper.py   # Base scraper class
│   │   │   ├── amazon_scraper.py # Amazon scraper
│   │   │   └── blinkit_scraper.py # Blinkit scraper
│   │   └── cart/                 # Cart management services
│   │       ├── __init__.py
│   │       └── cart_service.py   # Cart business logic
│   └── utils/                    # Helper functions (future)
├── tests/                        # Test files (future)
├── logs/                         # Application logs (created at runtime)
├── main.py                       # FastAPI application entry point
├── requirements.txt              # Python dependencies
├── env.example                   # Environment variables template
├── run_local.py                  # Local development startup script
├── start.bat                     # Windows startup script
├── start.sh                      # Unix/Linux/macOS startup script
├── start.py                      # Quick start script
├── test_basic.py                 # Basic functionality tests
├── README.md                     # Project documentation
└── PROJECT_STRUCTURE.md          # This file
```

## 🏗️ Architecture Overview

### Core Components

1. **FastAPI Application** (`main.py`)
   - Main application entry point
   - CORS middleware configuration
   - Database connection lifecycle management

2. **Configuration** (`app/core/config.py`)
   - Environment-based settings using Pydantic
   - Database, Redis, API keys, and platform configurations

3. **Data Models** (`app/models/`)
   - **Product Models**: Product, ProductPrice, ProductRating, DeliveryInfo
   - **Cart Models**: Cart, CartItem, CartOptimization
   - **API Models**: Request/Response models for all endpoints

4. **Database Layer** (`app/database/`)
   - MongoDB connection with Motor (async)
   - Collection management utilities

### Service Layer

1. **Search Service** (`app/services/search_service.py`)
   - Coordinates searches across multiple platforms
   - Handles concurrent scraping
   - Applies filters and sorting

2. **NLP Service** (`app/services/nlp/`)
   - Natural language query parsing
   - OpenAI API integration
   - Fallback keyword extraction

3. **Scraping Services** (`app/services/scrapers/`)
   - **Base Scraper**: Common scraping functionality
   - **Platform Scrapers**: Amazon, Blinkit, etc.
   - Async HTTP requests with retry logic

4. **Cart Service** (`app/services/cart/`)
   - Cart CRUD operations
   - Cart optimization algorithms
   - Platform selection logic

### API Layer

1. **Search Endpoints** (`app/api/v1/endpoints/search.py`)
   - `GET /api/v1/search/` - Product search
   - `GET /api/v1/search/platforms` - Available platforms
   - `GET /api/v1/search/product/{platform}/{id}` - Product details

2. **Cart Endpoints** (`app/api/v1/endpoints/cart.py`)
   - `POST /api/v1/cart/` - Create cart
   - `GET /api/v1/cart/{id}` - Get cart
   - `POST /api/v1/cart/{id}/add` - Add item
   - `DELETE /api/v1/cart/{id}/remove/{item_id}` - Remove item
   - `PUT /api/v1/cart/{id}/update/{item_id}` - Update quantity
   - `DELETE /api/v1/cart/{id}/clear` - Clear cart
   - `GET /api/v1/cart/{id}/summary` - Cart summary
   - `POST /api/v1/cart/{id}/optimize` - Optimize cart

3. **Query Endpoints** (`app/api/v1/endpoints/query.py`)
   - `POST /api/v1/query/parse` - Parse natural language
   - `POST /api/v1/query/keywords` - Extract keywords

## 🔧 Key Features

### 1. Multi-Platform Product Search
- **E-commerce**: Amazon, Flipkart, Meesho, Nykaa
- **Quick Commerce**: Blinkit, Zepto, Instamart
- Concurrent scraping with rate limiting
- Location-aware results

### 2. Natural Language Processing
- OpenAI GPT integration for query parsing
- Fallback keyword extraction
- Product intent recognition
- Constraint extraction (price, rating, delivery)

### 3. Smart Cart Management
- Universal cart across platforms
- Cart optimization algorithms
- Price vs. speed optimization
- Platform consolidation

### 4. Advanced Features
- Real-time price comparison
- Delivery time optimization
- Rating-based filtering
- Budget constraints
- Location-based search

### 1. Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
cp env.example .env
# Edit .env with your settings

# Start the application
python run_local.py
```

### 2. Quick Start Scripts
```bash
# Windows
start.bat

# Unix/Linux/macOS
./start.sh
```

## 📊 Data Flow

1. **User Query** → NLP Parser → Structured Intent
2. **Intent** → Search Service → Multiple Platform Scrapers
3. **Results** → Filtering/Sorting → Product Comparison
4. **Selection** → Cart Service → Cart Management
5. **Optimization** → Cart Optimization → Best Platform Selection

## 🔒 Security Considerations

- Rate limiting on API endpoints
- Input validation with Pydantic
- CORS configuration
- Environment variable management
- Environment variable management
- Request timeout handling

## 📈 Scalability Features

- Async/await throughout the application
- Connection pooling for databases
- Caching with Redis
- Concurrent scraping with limits
- Modular scraper architecture
- Horizontal scaling ready

## 🧪 Testing Strategy

- Unit tests for services
- Integration tests for API endpoints
- Mock testing for external APIs
- Performance testing for scrapers
- End-to-end testing for cart flows

## 🔄 Future Enhancements

1. **Additional Platforms**: More e-commerce and quick commerce platforms
2. **Price Alerts**: Monitor price drops
3. **User Authentication**: JWT-based auth system
4. **Analytics**: Search and purchase analytics
5. **Mobile App**: React Native frontend
6. **Voice Assistant**: Alexa/Google Assistant integration
7. **Telegram Bot**: Shopping via Telegram
8. **Chrome Extension**: Browser integration 