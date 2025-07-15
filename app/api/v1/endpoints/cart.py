from fastapi import APIRouter, HTTPException, Query, Body
from typing import Optional
import logging

from app.models.cart import (
    Cart, CartItem, CartOptimizationRequest, CartOptimizationResult, 
    CartOptimizationMode, CartResponse, CartSummary
)
from app.models.product import Product
from app.services.cart.cart_service import cart_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=CartResponse)
async def create_cart(
    user_id: Optional[str] = Body(None, description="User ID"),
    session_id: Optional[str] = Body(None, description="Session ID")
):
    """
    Create a new shopping cart.
    
    Either user_id or session_id should be provided to identify the cart owner.
    """
    try:
        cart = await cart_service.create_cart(user_id=user_id, session_id=session_id)
        return CartResponse(
            success=True,
            data=cart,
            message="Cart created successfully"
        )
    except Exception as e:
        logger.error(f"Error creating cart: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{cart_id}", response_model=CartResponse)
async def get_cart(cart_id: str):
    """
    Get cart by ID.
    """
    try:
        cart = await cart_service.get_cart(cart_id)
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")
        
        return CartResponse(
            success=True,
            data=cart,
            message="Cart retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting cart: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}", response_model=CartResponse)
async def get_user_cart(user_id: str):
    """
    Get cart by user ID.
    """
    try:
        cart = await cart_service.get_user_cart(user_id)
        if not cart:
            raise HTTPException(status_code=404, detail="User cart not found")
        
        return CartResponse(
            success=True,
            data=cart,
            message="User cart retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user cart: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{cart_id}/add", response_model=CartResponse)
async def add_item_to_cart(
    cart_id: str,
    product: Product = Body(..., description="Product to add"),
    quantity: int = Body(1, ge=1, description="Quantity to add"),
    selected_platform: Optional[str] = Body(None, description="Platform to use")
):
    """
    Add item to cart.
    """
    try:
        from app.models.product import Platform
        
        platform = None
        if selected_platform:
            try:
                platform = Platform(selected_platform)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid platform: {selected_platform}")
        
        success = await cart_service.add_item_to_cart(
            cart_id=cart_id,
            product=product,
            quantity=quantity,
            selected_platform=platform
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Cart not found")
        
        # Get updated cart
        cart = await cart_service.get_cart(cart_id)
        
        return CartResponse(
            success=True,
            data=cart,
            message="Item added to cart successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding item to cart: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{cart_id}/remove/{item_id}", response_model=CartResponse)
async def remove_item_from_cart(cart_id: str, item_id: str):
    """
    Remove item from cart.
    """
    try:
        success = await cart_service.remove_item_from_cart(cart_id, item_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Cart or item not found")
        
        # Get updated cart
        cart = await cart_service.get_cart(cart_id)
        
        return CartResponse(
            success=True,
            data=cart,
            message="Item removed from cart successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing item from cart: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{cart_id}/update/{item_id}", response_model=CartResponse)
async def update_item_quantity(
    cart_id: str,
    item_id: str,
    quantity: int = Body(..., ge=1, description="New quantity")
):
    """
    Update item quantity in cart.
    """
    try:
        success = await cart_service.update_item_quantity(cart_id, item_id, quantity)
        
        if not success:
            raise HTTPException(status_code=404, detail="Cart or item not found")
        
        # Get updated cart
        cart = await cart_service.get_cart(cart_id)
        
        return CartResponse(
            success=True,
            data=cart,
            message="Item quantity updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating item quantity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{cart_id}/clear", response_model=CartResponse)
async def clear_cart(cart_id: str):
    """
    Clear all items from cart.
    """
    try:
        success = await cart_service.clear_cart(cart_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Cart not found")
        
        # Get updated cart
        cart = await cart_service.get_cart(cart_id)
        
        return CartResponse(
            success=True,
            data=cart,
            message="Cart cleared successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing cart: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{cart_id}/summary")
async def get_cart_summary(cart_id: str):
    """
    Get cart summary with totals and statistics.
    """
    try:
        cart = await cart_service.get_cart(cart_id)
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")
        
        summary = CartSummary(
            total_items=cart.total_items,
            total_price=cart.total_price,
            total_original_price=cart.total_original_price,
            total_savings=cart.total_savings,
            platforms_used=cart.platforms_used,
            delivery_summary=cart.delivery_summary,
            item_count=len(cart.items)
        )
        
        return {
            "success": True,
            "data": summary,
            "message": "Cart summary retrieved successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting cart summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{cart_id}/optimize")
async def optimize_cart(
    cart_id: str,
    optimization_request: CartOptimizationRequest
):
    """
    Optimize cart based on specified criteria.
    
    Optimization modes:
    - best_price: Choose cheapest options
    - fastest_delivery: Choose fastest delivery options
    - minimum_platforms: Minimize number of platforms used
    - balanced: Balance between price and speed
    """
    try:
        result = await cart_service.optimize_cart(cart_id, optimization_request)
        
        if not result:
            raise HTTPException(status_code=404, detail="Cart not found or empty")
        
        return {
            "success": True,
            "data": result,
            "message": "Cart optimized successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error optimizing cart: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 