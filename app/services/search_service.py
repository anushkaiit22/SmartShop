import asyncio
import time
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import logging

from app.models.product import Product, ProductSearchRequest, ProductSearchResponse, ProductComparison, Platform
from app.services.scrapers.flipkart_scraper import FlipkartScraper
from app.services.scrapers.mock_scraper import MockAmazonScraper, MockMeeshoScraper, MockBlinkitScraper
from app.services.nlp.query_parser import query_parser
from app.core.config import settings

logger = logging.getLogger(__name__)


class SearchService:
    """Main service for coordinating product searches across platforms"""
    
    def __init__(self):
        # We don't initialize scrapers here - we'll create them as needed
        pass
    
    async def search_products(self, request: ProductSearchRequest) -> ProductSearchResponse:
        """Search for products across multiple platforms"""
        start_time = time.time()
        
        try:
            # Parse natural language query if needed
            parsed_constraints = None
            if self._is_natural_language(request.query):
                parsed_query = await query_parser.parse_query(request.query)
                # Use parsed products for search
                search_queries = [product.product_name for product in parsed_query.products]
                parsed_constraints = parsed_query.constraints
                
                # Use parsed price constraints if explicit max_price is not provided
                if request.max_price is None and parsed_constraints.total_budget:
                    request.max_price = parsed_constraints.total_budget
                    
                # Use parsed rating constraints if explicit min_rating is not provided
                if request.min_rating is None:
                    # Check if any product has min_rating specified
                    for product in parsed_query.products:
                        if product.min_rating:
                            request.min_rating = product.min_rating
                            break
            else:
                search_queries = [request.query]
            
            # Determine which platforms to search
            platforms_to_search = request.platforms or [Platform.AMAZON, Platform.FLIPKART, Platform.MEESHO, Platform.BLINKIT]
            
            all_products = []
            
            # Search across platforms with proper async context managers
            for platform in platforms_to_search:
                try:
                    if platform == Platform.AMAZON:
                        async with MockAmazonScraper() as scraper:
                            products = await scraper.search_products(request.query, request.limit)
                            logger.info(f"Amazon (Mock): Found {len(products)} products")
                    elif platform == Platform.FLIPKART:
                        async with FlipkartScraper() as scraper:
                            products = await scraper.search_products(request.query, request.limit)
                            logger.info(f"Flipkart (Real): Found {len(products)} products")
                    elif platform == Platform.MEESHO:
                        async with MockMeeshoScraper() as scraper:
                            products = await scraper.search_products(request.query, request.limit)
                            logger.info(f"Meesho (Mock): Found {len(products)} products")
                    elif platform == Platform.BLINKIT:
                        async with MockBlinkitScraper() as scraper:
                            products = await scraper.search_products(request.query, request.limit)
                            logger.info(f"Blinkit (Mock): Found {len(products)} products")
                    else:
                        logger.warning(f"Platform {platform.value} not supported")
                        continue
                    all_products.extend(products)
                except Exception as e:
                    logger.error(f"Error searching {platform.value}: {e}")
                    continue
            
            # Apply filters
            filtered_products = self._apply_filters(all_products, request)
            
            # Sort and limit results
            sorted_products = self._sort_products(filtered_products, request)
            limited_products = sorted_products[:request.limit]
            
            search_time = time.time() - start_time
            
            # Create response
            comparison = ProductComparison(
                query=request.query,
                products=limited_products,
                total_results=len(limited_products),
                search_time=search_time,
                location=request.location
            )
            
            return ProductSearchResponse(
                success=True,
                data=comparison,
                message=f"Found {len(limited_products)} products across {len(platforms_to_search)} platforms (Flipkart: Real, Others: Demo Data)"
            )
        
        except Exception as e:
            logger.error(f"Search service error: {e}")
            return ProductSearchResponse(
                success=False,
                error=str(e),
                message="Failed to search products"
            )
    
    def _is_natural_language(self, query: str) -> bool:
        """Check if query is natural language"""
        # Simple heuristic: if query contains common shopping words, it's likely natural language
        shopping_words = ['need', 'want', 'buy', 'get', 'find', 'looking for', 'search for']
        return any(word in query.lower() for word in shopping_words)
    
    def _apply_filters(self, products: List[Product], request: ProductSearchRequest) -> List[Product]:
        """Apply filters to products"""
        filtered_products = products
        
        # Price filter
        if request.max_price:
            filtered_products = [
                p for p in filtered_products 
                if p.price.current_price <= request.max_price
            ]
        
        # Rating filter
        if request.min_rating:
            filtered_products = [
                p for p in filtered_products 
                if p.rating and p.rating.rating >= request.min_rating
            ]
        
        # Category filter
        if request.category:
            filtered_products = [
                p for p in filtered_products 
                if p.category and request.category.lower() in p.category.lower()
            ]
        
        return filtered_products
    
    def _sort_products(self, products: List[Product], request: ProductSearchRequest) -> List[Product]:
        """Sort products based on various criteria"""
        # Default sorting: by price (lowest first)
        sorted_products = sorted(products, key=lambda p: p.price.current_price)
        
        # If delivery preference is specified, prioritize accordingly
        if hasattr(request, 'delivery_preference'):
            if request.delivery_preference == 'fast':
                # Sort by delivery time (quick commerce first, then by delivery time)
                sorted_products.sort(key=lambda p: (
                    p.platform_type.value != 'quick_commerce',
                    self._parse_delivery_time(p.delivery.delivery_time)
                ))
            elif request.delivery_preference == 'cheap':
                # Sort by price (lowest first)
                sorted_products.sort(key=lambda p: p.price.current_price)
        
        return sorted_products
    
    def _parse_delivery_time(self, delivery_time: str) -> int:
        """Parse delivery time to minutes for sorting"""
        import re
        
        # Extract minutes from delivery time string
        if 'min' in delivery_time.lower():
            match = re.search(r'(\d+)', delivery_time)
            return int(match.group(1)) if match else 999
        elif 'hour' in delivery_time.lower():
            match = re.search(r'(\d+)', delivery_time)
            return int(match.group(1)) * 60 if match else 999
        elif 'day' in delivery_time.lower():
            match = re.search(r'(\d+)', delivery_time)
            return int(match.group(1)) * 1440 if match else 999  # 24 * 60 minutes
        else:
            return 999  # Default high value for unknown formats
    
    async def get_product_details(self, platform: Platform, product_id: str, url: str) -> Optional[Product]:
        """Get detailed product information"""
        try:
            # This method will need to be updated to use Playwright or a new scraper
            # For now, it will return None as the scrapers are no longer Playwright-based
            logger.warning(f"get_product_details is not fully implemented for non-Playwright scrapers. Returning None for {product_id}")
            return None
                
        except Exception as e:
            logger.error(f"Error getting product details for {product_id}: {e}")
            return None
    
    def get_available_platforms(self) -> List[Platform]:
        """Get list of available platforms"""
        return [Platform.AMAZON, Platform.FLIPKART, Platform.MEESHO, Platform.BLINKIT]


# Global instance
search_service = SearchService() 