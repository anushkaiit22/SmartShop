from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import asyncio
import aiohttp
import logging
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time
from app.models.product import Product, Platform, PlatformType, ProductPrice, ProductRating, DeliveryInfo, ProductImage, ProductOffer
from app.core.config import settings

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Base class for all platform scrapers"""
    
    def __init__(self):
        self.ua = UserAgent()
        self.session: Optional[aiohttp.ClientSession] = None
        self.timeout = aiohttp.ClientTimeout(total=settings.SCRAPER_TIMEOUT)
        self.delay = settings.SCRAPER_DELAY
    
    async def __aenter__(self):
        """Async context manager entry"""
        # More realistic headers to avoid detection
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        self.session = aiohttp.ClientSession(
            timeout=self.timeout,
            headers=headers
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    @abstractmethod
    def get_platform(self) -> Platform:
        """Return the platform this scraper handles"""
        pass
    
    @abstractmethod
    def get_platform_type(self) -> PlatformType:
        """Return the platform type (ecommerce or quick_commerce)"""
        pass
    
    @abstractmethod
    def get_search_url(self, query: str, **kwargs) -> str:
        """Generate search URL for the platform"""
        pass
    
    @abstractmethod
    def parse_search_results(self, html: str, query: str) -> List[Product]:
        """Parse search results from HTML"""
        pass
    
    @abstractmethod
    def parse_product_page(self, html: str, product_id: str) -> Optional[Product]:
        """Parse individual product page"""
        pass
    
    async def search_products(self, query: str, limit: int = 10, **kwargs) -> List[Product]:
        """Search for products on the platform"""
        try:
            url = self.get_search_url(query, **kwargs)
            html = await self._fetch_page(url)
            
            if not html:
                logger.warning(f"Failed to fetch search results for {query} on {self.get_platform().value}")
                return []
            
            products = self.parse_search_results(html, query)
            
            # Apply limit
            products = products[:limit]
            
            # Add platform info
            for product in products:
                product.platform = self.get_platform()
                product.platform_type = self.get_platform_type()
            
            logger.info(f"Found {len(products)} products for '{query}' on {self.get_platform().value}")
            return products
            
        except Exception as e:
            logger.error(f"Error searching products on {self.get_platform().value}: {e}")
            return []
    
    async def get_product_details(self, product_id: str, url: str) -> Optional[Product]:
        """Get detailed product information"""
        try:
            html = await self._fetch_page(url)
            
            if not html:
                logger.warning(f"Failed to fetch product details for {product_id}")
                return None
            
            product = self.parse_product_page(html, product_id)
            
            if product:
                product.platform = self.get_platform()
                product.platform_type = self.get_platform_type()
            
            return product
            
        except Exception as e:
            logger.error(f"Error getting product details for {product_id}: {e}")
            return None
    
    async def _fetch_page(self, url: str) -> Optional[str]:
        """Fetch page content with retry logic"""
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        # Rotate user agents to avoid detection
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        
        for attempt in range(3):
            try:
                # Add delay between requests
                if attempt > 0:
                    await asyncio.sleep(self.delay * (attempt + 1))
                
                # Update user agent for each attempt
                self.session._default_headers['User-Agent'] = user_agents[attempt % len(user_agents)]
                
                async with self.session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        if len(content) > 1000:  # Basic check for valid content
                            return content
                        else:
                            logger.warning(f"Received suspiciously small content ({len(content)} chars) from {url}")
                    elif response.status == 429:  # Rate limited
                        wait_time = int(response.headers.get('Retry-After', 60))
                        logger.warning(f"Rate limited, waiting {wait_time} seconds")
                        await asyncio.sleep(wait_time)
                    elif response.status == 503:  # Service unavailable
                        logger.warning(f"Service unavailable (503) on attempt {attempt + 1} for {url}")
                        if attempt == 2:  # Last attempt
                            logger.error(f"Failed to access {url} after 3 attempts - likely blocked by anti-bot protection")
                    else:
                        logger.warning(f"HTTP {response.status} for {url}")
                        
            except asyncio.TimeoutError:
                logger.warning(f"Timeout on attempt {attempt + 1} for {url}")
            except Exception as e:
                logger.error(f"Error fetching {url}: {e}")
        
        return None
    
    def _extract_price(self, text: str) -> Optional[float]:
        """Extract price from text"""
        import re
        
        # Remove currency symbols and extract numbers
        price_pattern = r'[₹$]?\s*([\d,]+(?:\.\d{2})?)'
        match = re.search(price_pattern, text.replace(',', ''))
        
        if match:
            return float(match.group(1))
        return None
    
    def _extract_rating(self, text: str) -> Optional[float]:
        """Extract rating from text"""
        import re
        
        # Look for patterns like "4.5 out of 5", "4.5/5", "4.5"
        rating_patterns = [
            r'(\d+\.?\d*)\s*out\s*of\s*5',
            r'(\d+\.?\d*)/5',
            r'(\d+\.?\d*)\s*stars?',
            r'(\d+\.?\d*)'
        ]
        
        for pattern in rating_patterns:
            match = re.search(pattern, text)
            if match:
                rating = float(match.group(1))
                if 0 <= rating <= 5:
                    return rating
        
        return None
    
    def _extract_delivery_time(self, text: str) -> str:
        """Extract delivery time from text"""
        import re
        
        # Common delivery time patterns
        patterns = [
            r'(\d+)\s*(?:min|minute)s?',
            r'(\d+)\s*(?:hour)s?',
            r'(\d+)\s*(?:day)s?',
            r'(\d+)\s*(?:week)s?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                value = int(match.group(1))
                if 'min' in pattern:
                    return f"{value} mins"
                elif 'hour' in pattern:
                    return f"{value} hours"
                elif 'day' in pattern:
                    return f"{value} days"
                elif 'week' in pattern:
                    return f"{value} weeks"
        
        # Default delivery times based on platform type
        if self.get_platform_type() == PlatformType.QUICK_COMMERCE:
            return "10-30 mins"
        else:
            return "2-5 days"
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = ' '.join(text.split())
        return text.strip()
    
    def _extract_images(self, soup: BeautifulSoup, selector: str) -> List[ProductImage]:
        """Extract product images from soup"""
        images = []
        img_elements = soup.select(selector)
        
        for i, img in enumerate(img_elements):
            src = img.get('src') or img.get('data-src')
            if src:
                # Convert relative URLs to absolute
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    src = 'https://' + self.get_base_domain() + src
                
                images.append(ProductImage(
                    url=src,
                    alt_text=img.get('alt', ''),
                    is_primary=(i == 0)
                ))
        
        return images
    
    @abstractmethod
    def get_base_domain(self) -> str:
        """Return the base domain for the platform"""
        pass 