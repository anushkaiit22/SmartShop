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
    """Main service for coordinating product searches across platforms with Vercel-optimized fallbacks"""
    
    def __init__(self):
        # We don't initialize scrapers here - we'll create them as needed
        pass
    
    async def search_products(self, request: ProductSearchRequest) -> ProductSearchResponse:
        """Search for products across multiple platforms with Vercel-optimized fallbacks"""
        start_time = time.time()
        
        try:
            # Parse natural language query if needed
            parsed_constraints = None
            if self._is_natural_language(request.query):
                try:
                    parsed_query = await asyncio.wait_for(
                        query_parser.parse_query(request.query),
                        timeout=3.0  # Reduced timeout for Vercel
                    )
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
                except (asyncio.TimeoutError, Exception) as e:
                    logger.warning(f"NLP parsing failed, using direct query: {e}")
                    search_queries = [request.query]
            else:
                search_queries = [request.query]
            
            # Determine which platforms to search
            platforms_to_search = request.platforms or [Platform.FLIPKART, Platform.AMAZON, Platform.MEESHO, Platform.BLINKIT]
            
            all_products = []
            
            # For Vercel, prioritize mock data for speed
            if settings.IS_VERCEL:
                # Try mock scrapers first for faster response
                mock_products = await self._search_with_mock_scrapers(request, platforms_to_search)
                if mock_products:
                    all_products.extend(mock_products)
                    logger.info(f"Vercel: Found {len(mock_products)} products from mock scrapers")
                
                # Only try real scrapers if we have time and no mock products
                if not all_products:
                    real_products = await self._search_with_real_scrapers_vercel(request, platforms_to_search)
                    if real_products:
                        all_products.extend(real_products)
                        logger.info(f"Vercel: Found {len(real_products)} products from real scrapers")
            else:
                # Local development: try real scrapers first
                real_products = await self._search_with_real_scrapers(request, platforms_to_search)
                if real_products:
                    all_products.extend(real_products)
                    logger.info(f"Local: Found {len(real_products)} products from real scrapers")
                
                # Fall back to mock scrapers if needed
                if not all_products and settings.ENABLE_MOCK_FALLBACK:
                    mock_products = await self._search_with_mock_scrapers(request, platforms_to_search)
                    if mock_products:
                        all_products.extend(mock_products)
                        logger.info(f"Local: Found {len(mock_products)} products from mock scrapers (fallback)")
            
            # If still no products, create basic mock products based on query
            if not all_products:
                basic_products = self._create_basic_mock_products(request.query, platforms_to_search)
                all_products.extend(basic_products)
                logger.info(f"Created {len(basic_products)} basic mock products")
            
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
            
            # Determine response message based on data source
            if settings.IS_VERCEL:
                if mock_products:
                    message = f"Found {len(limited_products)} products (demo data - optimized for speed)"
                elif real_products:
                    message = f"Found {len(limited_products)} products across {len(platforms_to_search)} platforms"
                else:
                    message = f"Found {len(limited_products)} products (basic demo data)"
            else:
                if real_products:
                    message = f"Found {len(limited_products)} products across {len(platforms_to_search)} platforms"
                elif mock_products:
                    message = f"Found {len(limited_products)} products (demo data - real search unavailable)"
                else:
                    message = f"Found {len(limited_products)} products (basic demo data)"
            
            return ProductSearchResponse(
                success=True,
                data=comparison,
                message=message
            )
        
        except Exception as e:
            logger.error(f"Search service error: {e}")
            # Return mock data as final fallback
            fallback_products = self._create_basic_mock_products(request.query, [Platform.FLIPKART])
            return ProductSearchResponse(
                success=True,
                data=ProductComparison(
                    query=request.query,
                    products=fallback_products[:request.limit],
                    total_results=len(fallback_products),
                    search_time=time.time() - start_time,
                    location=request.location
                ),
                message=f"Using demo data due to search error: {str(e)}"
            )
    
    async def _search_with_real_scrapers_vercel(self, request: ProductSearchRequest, platforms: List[Platform]) -> List[Product]:
        """Search with real scrapers optimized for Vercel (shorter timeout)"""
        all_products = []
        
        # Only try Flipkart on Vercel for speed
        if Platform.FLIPKART in platforms:
            try:
                products = await asyncio.wait_for(
                    self._search_flipkart(request.query, request.limit),
                    timeout=settings.SCRAPER_TIMEOUT - settings.VERCEL_TIMEOUT_BUFFER
                )
                all_products.extend(products)
            except (asyncio.TimeoutError, Exception) as e:
                logger.warning(f"Vercel: Flipkart scraper failed: {e}")
        
        return all_products
    
    async def _search_with_real_scrapers(self, request: ProductSearchRequest, platforms: List[Platform]) -> List[Product]:
        """Search with real scrapers with timeout"""
        all_products = []
        
        # Create tasks for concurrent scraping
        tasks = []
        for platform in platforms:
            if platform == Platform.FLIPKART:
                tasks.append(self._search_flipkart(request.query, request.limit))
            # Add other real scrapers here when available
        
        # Execute with timeout
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=settings.SCRAPER_TIMEOUT
            )
            
            for result in results:
                if isinstance(result, list):
                    all_products.extend(result)
                elif isinstance(result, Exception):
                    logger.warning(f"Real scraper error: {result}")
                    
        except asyncio.TimeoutError:
            logger.warning("Real scrapers timed out, falling back to mock data")
        except Exception as e:
            logger.error(f"Error with real scrapers: {e}")
        
        return all_products
    
    async def _search_flipkart(self, query: str, limit: int) -> List[Product]:
        """Search Flipkart with timeout"""
        try:
            async with FlipkartScraper() as scraper:
                return await scraper.search_products(query, limit)
        except Exception as e:
            logger.error(f"Flipkart scraper error: {e}")
            return []
    
    async def _search_with_mock_scrapers(self, request: ProductSearchRequest, platforms: List[Platform]) -> List[Product]:
        """Search with mock scrapers (fast fallback)"""
        all_products = []
        
        # Limit to 2 platforms for speed on Vercel
        platforms_to_search = platforms[:2] if settings.IS_VERCEL else platforms
        
        for platform in platforms_to_search:
            try:
                if platform == Platform.AMAZON:
                    async with MockAmazonScraper() as scraper:
                        products = await scraper.search_products(request.query, request.limit)
                        all_products.extend(products)
                elif platform == Platform.MEESHO:
                    async with MockMeeshoScraper() as scraper:
                        products = await scraper.search_products(request.query, request.limit)
                        all_products.extend(products)
                elif platform == Platform.BLINKIT:
                    async with MockBlinkitScraper() as scraper:
                        products = await scraper.search_products(request.query, request.limit)
                        all_products.extend(products)
                        
                # Add small delay for mock scrapers
                await asyncio.sleep(settings.MOCK_FALLBACK_DELAY)
                
            except Exception as e:
                logger.error(f"Mock scraper error for {platform.value}: {e}")
                continue
        
        return all_products
    
    def _create_basic_mock_products(self, query: str, platforms: List[Platform]) -> List[Product]:
        """Create basic mock products when all else fails"""
        products = []
        
        # Common product templates based on query
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['cheese', 'dairy', 'milk']):
            product_names = [
                f"Amul {query.title()} - 200g",
                f"Britannia {query.title()} - 250g", 
                f"Mother Dairy {query.title()} - 500g"
            ]
        elif any(word in query_lower for word in ['phone', 'mobile', 'smartphone']):
            product_names = [
                f"iPhone 15 - 128GB",
                f"Samsung Galaxy S24 - 256GB",
                f"OnePlus 12 - 512GB"
            ]
        elif any(word in query_lower for word in ['laptop', 'computer']):
            product_names = [
                f"MacBook Air M2 - 13 inch",
                f"Dell Inspiron 15 - Intel i5",
                f"HP Pavilion 14 - AMD Ryzen 5"
            ]
        else:
            product_names = [
                f"{query.title()} - Premium Quality",
                f"{query.title()} - Best Seller",
                f"{query.title()} - Value Pack"
            ]
        
        base_prices = [299, 499, 799, 1299, 1999, 2999]
        
        # Limit to 2 platforms for speed on Vercel
        platforms_to_use = platforms[:2] if settings.IS_VERCEL else platforms[:3]
        
        for i, platform in enumerate(platforms_to_use):
            for j, name in enumerate(product_names):
                if len(products) >= (4 if settings.IS_VERCEL else 6):  # Limit products for Vercel
                    break
                    
                price = base_prices[(i + j) % len(base_prices)]
                
                product = Product(
                    name=name,
                    platform=platform,
                    platform_type=PlatformType.ECOMMERCE if platform != Platform.BLINKIT else PlatformType.QUICK_COMMERCE,
                    platform_product_id=f"mock_{platform.value}_{i}_{j}",
                    platform_url=f"https://{platform.value}.com/product/{i}_{j}",
                    price=ProductPrice(
                        current_price=price,
                        original_price=price * 1.2,
                        currency="INR"
                    ),
                    rating=ProductRating(
                        rating=4.0 + (i + j) * 0.1,
                        total_ratings=100 + (i + j) * 50
                    ),
                    images=[ProductImage(url=f"https://via.placeholder.com/300x300?text={name.replace(' ', '+')}")],
                    delivery=DeliveryInfo(
                        delivery_time="2-3 days" if platform != Platform.BLINKIT else "10-30 mins",
                        delivery_cost=0.0 if platform != Platform.BLINKIT else 20.0,
                        is_free_delivery=True if platform != Platform.BLINKIT else False
                    )
                )
                products.append(product)
        
        return products
    
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