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
    
    # Database (optional for testing)
    MONGODB_URL: Optional[str] = None
    MONGODB_DB_NAME: str = "smartshop"
    
    # Redis (optional - for caching)
    REDIS_URL: Optional[str] = None
    
    # JWT
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000"
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
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings() 