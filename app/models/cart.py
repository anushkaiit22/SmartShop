from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from .product import Platform, Product


class CartItem(BaseModel):
    """Model for individual cart items"""
    id: Optional[str] = None
    product: Product
    quantity: int = Field(ge=1, default=1)
    selected_platform: Platform
    added_at: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None
    
    @property
    def total_price(self) -> float:
        """Calculate total price for this item"""
        return self.product.price.current_price * self.quantity
    
    @property
    def total_original_price(self) -> Optional[float]:
        """Calculate total original price for this item"""
        if self.product.price.original_price:
            return self.product.price.original_price * self.quantity
        return None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CartOptimizationMode(str, Enum):
    BEST_PRICE = "best_price"
    FASTEST_DELIVERY = "fastest_delivery"
    BALANCED = "balanced"
    MINIMUM_PLATFORMS = "minimum_platforms"


class CartOptimizationRequest(BaseModel):
    """Model for cart optimization requests"""
    mode: CartOptimizationMode = CartOptimizationMode.BALANCED
    max_total: Optional[float] = None
    max_platforms: Optional[int] = None
    prioritize_quick_delivery: bool = False


class CartOptimizationResult(BaseModel):
    """Model for cart optimization results"""
    original_total: float
    optimized_total: float
    savings: float
    delivery_time: str
    platforms_used: List[Platform]
    optimization_notes: List[str] = []
    cart_items: List[CartItem]


class Cart(BaseModel):
    """Main cart model"""
    id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    items: List[CartItem] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @property
    def total_items(self) -> int:
        """Get total number of items in cart"""
        return sum(item.quantity for item in self.items)
    
    @property
    def total_price(self) -> float:
        """Calculate total cart price"""
        return sum(item.total_price for item in self.items)
    
    @property
    def total_original_price(self) -> float:
        """Calculate total original price"""
        total = 0
        for item in self.items:
            if item.total_original_price:
                total += item.total_original_price
            else:
                total += item.total_price
        return total
    
    @property
    def total_savings(self) -> float:
        """Calculate total savings"""
        return self.total_original_price - self.total_price
    
    @property
    def platforms_used(self) -> List[Platform]:
        """Get list of platforms used in cart"""
        return list(set(item.selected_platform for item in self.items))
    
    @property
    def delivery_summary(self) -> Dict[str, Any]:
        """Get delivery summary"""
        delivery_times = {}
        for item in self.items:
            platform = item.selected_platform.value
            if platform not in delivery_times:
                delivery_times[platform] = []
            delivery_times[platform].append(item.product.delivery.delivery_time)
        
        return {
            "platforms": delivery_times,
            "fastest_delivery": min(
                [item.product.delivery.delivery_time for item in self.items],
                default="N/A"
            )
        }
    
    def add_item(self, item: CartItem) -> None:
        """Add item to cart"""
        # Check if item already exists with same product and platform
        existing_item = next(
            (cart_item for cart_item in self.items 
             if (cart_item.product.platform_product_id == item.product.platform_product_id and
                 cart_item.selected_platform == item.selected_platform)),
            None
        )
        
        if existing_item:
            existing_item.quantity += item.quantity
        else:
            self.items.append(item)
        
        self.updated_at = datetime.utcnow()
    
    def remove_item(self, item_id: str) -> bool:
        """Remove item from cart"""
        initial_length = len(self.items)
        self.items = [item for item in self.items if item.id != item_id]
        if len(self.items) < initial_length:
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def update_quantity(self, item_id: str, quantity: int) -> bool:
        """Update item quantity"""
        for item in self.items:
            if item.id == item_id:
                if quantity <= 0:
                    self.items.remove(item)
                else:
                    item.quantity = quantity
                self.updated_at = datetime.utcnow()
                return True
        return False
    
    def clear(self) -> None:
        """Clear all items from cart"""
        self.items = []
        self.updated_at = datetime.utcnow()
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CartResponse(BaseModel):
    """Model for cart API responses"""
    success: bool
    data: Optional[Cart] = None
    error: Optional[str] = None
    message: Optional[str] = None


class CartSummary(BaseModel):
    """Model for cart summary"""
    total_items: int
    total_price: float
    total_original_price: float
    total_savings: float
    platforms_used: List[Platform]
    delivery_summary: Dict[str, Any]
    item_count: int 