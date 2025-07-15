from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class PlatformType(str, Enum):
    ECOMMERCE = "ecommerce"
    QUICK_COMMERCE = "quick_commerce"


class Platform(str, Enum):
    AMAZON = "amazon"
    FLIPKART = "flipkart"
    BLINKIT = "blinkit"
    ZEPTO = "zepto"
    MEESHO = "meesho"
    NYKAA = "nykaa"
    INSTAMART = "instamart"


class ProductOffer(BaseModel):
    """Model for product offers and discounts"""
    discount_percentage: Optional[float] = None
    discount_amount: Optional[float] = None
    offer_text: Optional[str] = None
    coupon_code: Optional[str] = None
    valid_until: Optional[datetime] = None


class ProductRating(BaseModel):
    """Model for product ratings"""
    rating: float = Field(ge=0.0, le=5.0)
    total_reviews: int = Field(ge=0)
    rating_text: Optional[str] = None


class DeliveryInfo(BaseModel):
    """Model for delivery information"""
    delivery_time: str  # e.g., "10 mins", "2 days"
    delivery_fee: Optional[float] = None
    free_delivery: bool = False
    estimated_delivery: Optional[datetime] = None
    delivery_type: str = "standard"  # standard, express, same_day


class ProductPrice(BaseModel):
    """Model for product pricing"""
    current_price: float
    original_price: Optional[float] = None
    currency: str = "INR"
    price_per_unit: Optional[str] = None  # e.g., "₹50/kg"
    offers: List[ProductOffer] = []


class ProductImage(BaseModel):
    """Model for product images"""
    url: str
    alt_text: Optional[str] = None
    is_primary: bool = False


class Product(BaseModel):
    """Main product model"""
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    
    # Platform specific info
    platform: Platform
    platform_type: PlatformType
    platform_product_id: str
    platform_url: str
    
    # Pricing
    price: ProductPrice
    
    # Images
    images: List[ProductImage] = []
    
    # Ratings
    rating: Optional[ProductRating] = None
    
    # Delivery
    delivery: DeliveryInfo
    
    # Additional info
    specifications: Dict[str, Any] = {}
    availability: bool = True
    in_stock: bool = True
    stock_quantity: Optional[int] = None
    
    # Metadata
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    location: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ProductComparison(BaseModel):
    """Model for comparing products across platforms"""
    query: str
    products: List[Product]
    total_results: int
    search_time: float  # in seconds
    location: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ProductSearchRequest(BaseModel):
    """Model for product search requests"""
    query: str = Field(..., min_length=1, max_length=500)
    platforms: Optional[List[Platform]] = None
    max_price: Optional[float] = None
    min_rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    category: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    limit: int = Field(default=20, ge=1, le=100)


class ProductSearchResponse(BaseModel):
    """Model for product search responses"""
    success: bool
    data: Optional[ProductComparison] = None
    error: Optional[str] = None
    message: Optional[str] = None 