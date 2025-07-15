from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Optional
import logging
import subprocess
import json
import sys

from app.models.product import ProductSearchRequest, ProductSearchResponse, Platform, ProductComparison, Product, PlatformType
from app.services.search_service import search_service
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=ProductSearchResponse)
async def search_products(
    q: str = Query(..., description="Search query"),
    platforms: Optional[str] = Query(None, description="Comma-separated list of platforms"),
    max_price: Optional[float] = Query(None, description="Maximum price filter"),
    min_rating: Optional[float] = Query(None, description="Minimum rating filter"),
    category: Optional[str] = Query(None, description="Category filter"),
    location: Optional[str] = Query(None, description="Location for search"),
    latitude: Optional[float] = Query(None, description="Latitude for location-based search"),
    longitude: Optional[float] = Query(None, description="Longitude for location-based search"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results")
):
    """
    Search for products across multiple e-commerce platforms.
    
    This endpoint searches for products across Amazon, Flipkart, Blinkit, Zepto, and other platforms.
    It supports natural language queries and various filters.
    
    Example queries:
    - "laptop under 50000"
    - "milk and bread"
    - "smartphone with 4+ rating"
    """
    try:
        # Parse platforms
        platform_list = None
        if platforms:
            platform_names = [p.strip().lower() for p in platforms.split(",")]
            platform_list = []
            for name in platform_names:
                try:
                    platform_list.append(Platform(name))
                except ValueError:
                    logger.warning(f"Invalid platform: {name}")
        
        # Create search request
        request = ProductSearchRequest(
            query=q,
            platforms=platform_list,
            max_price=max_price,
            min_rating=min_rating,
            category=category,
            location=location,
            latitude=latitude,
            longitude=longitude,
            limit=limit
        )
        
        # Perform search
        response = await search_service.search_products(request)
        
        if not response.success:
            raise HTTPException(status_code=500, detail=response.error)
        
        return response
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=ProductSearchResponse)
async def search_products_post(request: ProductSearchRequest = Body(...)):
    """
    Search for products across multiple e-commerce platforms (POST).
    Accepts a JSON body.
    """
    try:
        response = await search_service.search_products(request)
        if not response.success:
            raise HTTPException(status_code=500, detail=response.error)
        return response
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/platforms")
async def get_available_platforms():
    """
    Get list of available platforms for searching.
    """
    try:
        platforms = search_service.get_available_platforms()
        return {
            "success": True,
            "platforms": [platform.value for platform in platforms],
            "total": len(platforms)
        }
    except Exception as e:
        logger.error(f"Error getting platforms: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/product/{platform}/{product_id}")
async def get_product_details(
    platform: str,
    product_id: str,
    url: str = Query(..., description="Product URL")
):
    """
    Get detailed product information from a specific platform.
    """
    try:
        # Validate platform
        try:
            platform_enum = Platform(platform)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid platform: {platform}")
        
        # Get product details
        product = await search_service.get_product_details(platform_enum, product_id, url)
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return {
            "success": True,
            "data": product
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product details: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 


 