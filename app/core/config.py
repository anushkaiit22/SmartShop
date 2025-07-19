from pydantic_settings import BaseSettings
from typing import List, Optional
import os
class Settings(BaseSettings):
    # Application
    APP_NAME: str = "SmartShop API"
    DEBUG: bool = False
    VERSION: str = "1.0.0"
    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    # Database (optional for testing - not used in Vercel deployment)
    MONGODB_URL: Optional[str] = None
    MONGODB_DB_NAME: str = "smartshop"
    # Redis (optional - for caching - not used in Vercel deployment)
    REDIS_URL: Optional[str] = None
    # JWT
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # CORS - Updated for Vercel deployment
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",  # Vite default port
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",  # Vite default port
        "http://127.0.0.1:8000",
        "https://smartshop-frontend.vercel.app",
        "https://smartshop-backend.vercel.app",
        "https://smart-shop-frontend-git-master-anushka-pimpales-projects.vercel.app",
        "https://smartshop-backend-3xenf4eub-anushka-pimpales-projects.vercel.app",
        # Add common Vercel patterns
        "https://smart-shop-frontend-*.vercel.app",
        "https://smartshop-backend-*.vercel.app"
    ]
    # Scraping
    SCRAPER_TIMEOUT: int = 30
    SCRAPER_DELAY: float = 1.0
    MAX_CONCURRENT_REQUESTS: int = 5
    # E-commerce Platforms
    ENABLED_PLATFORMS: List[str] = [
        "amazon",
        "flipkart", 
        "blinkit",
        "zepto",
        "meesho",
        "nykaa"
    ]
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    # Cache
    CACHE_TTL: int = 300  # 5 minutes
    # Location (default to Mumbai)
    DEFAULT_LATITUDE: float = 19.0760
    DEFAULT_LONGITUDE: float = 72.8777
    DEFAULT_CITY: str = "Mumbai"
    # Production settings
    PORT: int = int(os.getenv("PORT", 8000))
    HOST: str = "0.0.0.0"
    class Config:
        env_file = ".env"
        case_sensitive = True
# Create settings instance
settings = Settings() 