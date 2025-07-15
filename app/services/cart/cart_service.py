import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from app.models.cart import Cart, CartItem, CartOptimizationRequest, CartOptimizationResult, CartOptimizationMode
from app.models.product import Product, Platform, PlatformType
from app.core.config import settings

logger = logging.getLogger(__name__)


class CartService:
    """Service for managing shopping cart functionality"""
    
    def __init__(self):
        # In-memory storage for carts when MongoDB is not available
        self._carts: Dict[str, Cart] = {}
        
        # Try to get MongoDB collection, but don't fail if not available
        try:
            from app.database.mongodb import get_collection
            self.cart_collection = get_collection("carts")
            self.use_mongodb = True
        except RuntimeError:
            logger.info("MongoDB not available - using in-memory cart storage")
            self.cart_collection = None
            self.use_mongodb = False
    
    async def create_cart(self, user_id: Optional[str] = None, session_id: Optional[str] = None) -> Cart:
        """Create a new cart"""
        cart = Cart(
            id=str(uuid.uuid4()),
            user_id=user_id,
            session_id=session_id
        )
        
        if self.use_mongodb:
            # Save to database
            cart_dict = cart.dict()
            await self.cart_collection.insert_one(cart_dict)
        else:
            # Save to memory
            self._carts[cart.id] = cart
        
        return cart
    
    async def get_cart(self, cart_id: str) -> Optional[Cart]:
        """Get cart by ID"""
        try:
            if self.use_mongodb:
                cart_data = await self.cart_collection.find_one({"id": cart_id})
                if cart_data:
                    return Cart(**cart_data)
            else:
                return self._carts.get(cart_id)
            return None
        except Exception as e:
            logger.error(f"Error getting cart {cart_id}: {e}")
            return None
    
    async def get_user_cart(self, user_id: str) -> Optional[Cart]:
        """Get cart by user ID"""
        try:
            if self.use_mongodb:
                cart_data = await self.cart_collection.find_one({"user_id": user_id})
                if cart_data:
                    return Cart(**cart_data)
            else:
                # Find cart by user_id in memory
                for cart in self._carts.values():
                    if cart.user_id == user_id:
                        return cart
            return None
        except Exception as e:
            logger.error(f"Error getting user cart {user_id}: {e}")
            return None
    
    async def get_session_cart(self, session_id: str) -> Optional[Cart]:
        """Get cart by session ID"""
        try:
            if self.use_mongodb:
                cart_data = await self.cart_collection.find_one({"session_id": session_id})
                if cart_data:
                    return Cart(**cart_data)
            else:
                # Find cart by session_id in memory
                for cart in self._carts.values():
                    if cart.session_id == session_id:
                        return cart
            return None
        except Exception as e:
            logger.error(f"Error getting session cart {session_id}: {e}")
            return None
    
    async def add_item_to_cart(self, cart_id: str, product: Product, quantity: int = 1, 
                              selected_platform: Optional[Platform] = None) -> bool:
        """Add item to cart"""
        try:
            cart = await self.get_cart(cart_id)
            if not cart:
                return False
            
            # Use provided platform or product's platform
            platform = selected_platform or product.platform
            
            # Create cart item
            cart_item = CartItem(
                id=str(uuid.uuid4()),
                product=product,
                quantity=quantity,
                selected_platform=platform
            )
            
            # Add to cart
            cart.add_item(cart_item)
            
            if self.use_mongodb:
                # Update in database
                await self.cart_collection.update_one(
                    {"id": cart_id},
                    {"$set": {
                        "items": [item.dict() for item in cart.items],
                        "updated_at": cart.updated_at
                    }}
                )
            else:
                # Update in memory
                self._carts[cart_id] = cart
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding item to cart {cart_id}: {e}")
            return False
    
    async def remove_item_from_cart(self, cart_id: str, item_id: str) -> bool:
        """Remove item from cart"""
        try:
            cart = await self.get_cart(cart_id)
            if not cart:
                return False
            
            success = cart.remove_item(item_id)
            if success:
                if self.use_mongodb:
                    # Update in database
                    await self.cart_collection.update_one(
                        {"id": cart_id},
                        {"$set": {
                            "items": [item.dict() for item in cart.items],
                            "updated_at": cart.updated_at
                        }}
                    )
                else:
                    # Update in memory
                    self._carts[cart_id] = cart
            
            return success
            
        except Exception as e:
            logger.error(f"Error removing item from cart {cart_id}: {e}")
            return False
    
    async def update_item_quantity(self, cart_id: str, item_id: str, quantity: int) -> bool:
        """Update item quantity in cart"""
        try:
            cart = await self.get_cart(cart_id)
            if not cart:
                return False
            
            success = cart.update_quantity(item_id, quantity)
            if success:
                if self.use_mongodb:
                    # Update in database
                    await self.cart_collection.update_one(
                        {"id": cart_id},
                        {"$set": {
                            "items": [item.dict() for item in cart.items],
                            "updated_at": cart.updated_at
                        }}
                    )
                else:
                    # Update in memory
                    self._carts[cart_id] = cart
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating item quantity in cart {cart_id}: {e}")
            return False
    
    async def clear_cart(self, cart_id: str) -> bool:
        """Clear all items from cart"""
        try:
            cart = await self.get_cart(cart_id)
            if not cart:
                return False
            
            cart.clear()
            
            if self.use_mongodb:
                # Update in database
                await self.cart_collection.update_one(
                    {"id": cart_id},
                    {"$set": {
                        "items": [],
                        "updated_at": cart.updated_at
                    }}
                )
            else:
                # Update in memory
                self._carts[cart_id] = cart
            
            return True
            
        except Exception as e:
            logger.error(f"Error clearing cart {cart_id}: {e}")
            return False
    
    async def optimize_cart(self, cart_id: str, optimization_request: CartOptimizationRequest) -> Optional[CartOptimizationResult]:
        """Optimize cart based on specified criteria"""
        try:
            cart = await self.get_cart(cart_id)
            if not cart or not cart.items:
                return None
            
            original_total = cart.total_price
            original_items = cart.items.copy()
            
            # Apply optimization based on mode
            if optimization_request.mode == CartOptimizationMode.BEST_PRICE:
                optimized_items = self._optimize_for_price(cart.items, optimization_request)
            elif optimization_request.mode == CartOptimizationMode.FASTEST_DELIVERY:
                optimized_items = self._optimize_for_speed(cart.items, optimization_request)
            elif optimization_request.mode == CartOptimizationMode.MINIMUM_PLATFORMS:
                optimized_items = self._optimize_for_minimum_platforms(cart.items, optimization_request)
            else:  # BALANCED
                optimized_items = self._optimize_balanced(cart.items, optimization_request)
            
            # Calculate optimized total
            optimized_total = sum(item.total_price for item in optimized_items)
            savings = original_total - optimized_total
            
            # Calculate delivery time
            delivery_time = self._calculate_delivery_time(optimized_items)
            
            # Get platforms used
            platforms_used = list(set(item.selected_platform for item in optimized_items))
            
            # Generate optimization notes
            optimization_notes = self._generate_optimization_notes(
                original_items, optimized_items, optimization_request
            )
            
            return CartOptimizationResult(
                original_total=original_total,
                optimized_total=optimized_total,
                savings=savings,
                delivery_time=delivery_time,
                platforms_used=platforms_used,
                optimization_notes=optimization_notes,
                cart_items=optimized_items
            )
            
        except Exception as e:
            logger.error(f"Error optimizing cart {cart_id}: {e}")
            return None
    
    def _optimize_for_price(self, items: List[CartItem], request: CartOptimizationRequest) -> List[CartItem]:
        """Optimize cart for best price"""
        optimized_items = []
        
        # Group items by product name
        product_groups = {}
        for item in items:
            product_name = item.product.name.lower()
            if product_name not in product_groups:
                product_groups[product_name] = []
            product_groups[product_name].append(item)
        
        # For each product, choose the cheapest option
        for product_name, product_items in product_groups.items():
            cheapest_item = min(product_items, key=lambda x: x.total_price)
            optimized_items.append(cheapest_item)
        
        return optimized_items
    
    def _optimize_for_speed(self, items: List[CartItem], request: CartOptimizationRequest) -> List[CartItem]:
        """Optimize cart for fastest delivery"""
        optimized_items = []
        
        # Group items by product name
        product_groups = {}
        for item in items:
            product_name = item.product.name.lower()
            if product_name not in product_groups:
                product_groups[product_name] = []
            product_groups[product_name].append(item)
        
        # For each product, choose the fastest delivery option
        for product_name, product_items in product_groups.items():
            fastest_item = min(product_items, key=lambda x: self._parse_delivery_time(x.product.delivery.delivery_time))
            optimized_items.append(fastest_item)
        
        return optimized_items
    
    def _optimize_for_minimum_platforms(self, items: List[CartItem], request: CartOptimizationRequest) -> List[CartItem]:
        """Optimize cart to use minimum number of platforms"""
        # This is a simplified version - in practice, you'd need more sophisticated algorithms
        optimized_items = []
        
        # Group items by platform
        platform_groups = {}
        for item in items:
            platform = item.selected_platform
            if platform not in platform_groups:
                platform_groups[platform] = []
            platform_groups[platform].append(item)
        
        # Choose the platform with most items (simplified approach)
        if platform_groups:
            best_platform = max(platform_groups.keys(), key=lambda p: len(platform_groups[p]))
            optimized_items = platform_groups[best_platform]
        
        return optimized_items
    
    def _optimize_balanced(self, items: List[CartItem], request: CartOptimizationRequest) -> List[CartItem]:
        """Optimize cart with balanced approach"""
        # Combine price and speed optimization
        price_optimized = self._optimize_for_price(items, request)
        speed_optimized = self._optimize_for_speed(items, request)
        
        # Choose the better option based on user preference
        if request.prioritize_quick_delivery:
            return speed_optimized
        else:
            return price_optimized
    
    def _calculate_delivery_time(self, items: List[CartItem]) -> str:
        """Calculate overall delivery time for cart items"""
        if not items:
            return "N/A"
        
        # Get delivery times for all items
        delivery_times = []
        for item in items:
            time_str = item.product.delivery.delivery_time
            minutes = self._parse_delivery_time(time_str)
            delivery_times.append(minutes)
        
        # Return the longest delivery time (bottleneck)
        max_minutes = max(delivery_times)
        
        if max_minutes < 60:
            return f"{max_minutes} mins"
        elif max_minutes < 1440:  # 24 hours
            hours = max_minutes // 60
            return f"{hours} hours"
        else:
            days = max_minutes // 1440
            return f"{days} days"
    
    def _parse_delivery_time(self, delivery_time: str) -> int:
        """Parse delivery time to minutes"""
        import re
        
        if 'min' in delivery_time.lower():
            match = re.search(r'(\d+)', delivery_time)
            return int(match.group(1)) if match else 999
        elif 'hour' in delivery_time.lower():
            match = re.search(r'(\d+)', delivery_time)
            return int(match.group(1)) * 60 if match else 999
        elif 'day' in delivery_time.lower():
            match = re.search(r'(\d+)', delivery_time)
            return int(match.group(1)) * 1440 if match else 999
        else:
            return 999
    
    def _generate_optimization_notes(self, original_items: List[CartItem], 
                                   optimized_items: List[CartItem], 
                                   request: CartOptimizationRequest) -> List[str]:
        """Generate notes about the optimization"""
        notes = []
        
        # Count platform changes
        original_platforms = set(item.selected_platform for item in original_items)
        optimized_platforms = set(item.selected_platform for item in optimized_items)
        
        if len(optimized_platforms) < len(original_platforms):
            notes.append(f"Reduced platforms from {len(original_platforms)} to {len(optimized_platforms)}")
        
        # Check for quick commerce usage
        quick_commerce_items = [item for item in optimized_items 
                              if item.product.platform_type == PlatformType.QUICK_COMMERCE]
        if quick_commerce_items:
            notes.append(f"Using {len(quick_commerce_items)} items from quick commerce for faster delivery")
        
        # Price savings note
        original_total = sum(item.total_price for item in original_items)
        optimized_total = sum(item.total_price for item in optimized_items)
        if optimized_total < original_total:
            savings = original_total - optimized_total
            notes.append(f"Saved ₹{savings:.2f} through optimization")
        
        return notes


# Global instance
cart_service = CartService() 