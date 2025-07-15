import asyncio
import re
from typing import List, Optional, Dict, Any
from playwright.async_api import async_playwright, Page, Browser
import logging
from app.models.product import Product, Platform, PlatformType, ProductPrice, ProductRating, DeliveryInfo, ProductImage
from app.services.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class PlaywrightScraper(BaseScraper):
    """Playwright-based scraper for e-commerce platforms"""
    
    def __init__(self):
        super().__init__()
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
    
    # Required abstract methods from BaseScraper
    def get_platform(self) -> Platform:
        """Return the platform this scraper handles"""
        return Platform.AMAZON  # Default platform
    
    def get_platform_type(self) -> PlatformType:
        """Return the platform type"""
        return PlatformType.ECOMMERCE
    
    def get_base_domain(self) -> str:
        """Return the base domain"""
        return "amazon.in"  # Default domain
    
    def get_search_url(self, query: str, **kwargs) -> str:
        """Generate search URL for the platform"""
        encoded_query = query.replace(' ', '+')
        return f"https://www.amazon.in/s?k={encoded_query}"
    
    def parse_search_results(self, html: str, query: str) -> List[Product]:
        """Parse search results from HTML - not used in Playwright scraper"""
        # This method is not used in Playwright scraper as we extract directly from DOM
        return []
    
    def parse_product_page(self, html: str, product_id: str) -> Optional[Product]:
        """Parse individual product page - not used in Playwright scraper"""
        # This method is not used in Playwright scraper as we extract directly from DOM
        return None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu'
            ]
        )
        self.page = await self.browser.new_page()
        
        # Set realistic viewport and user agent
        await self.page.set_viewport_size({"width": 1920, "height": 1080})
        await self.page.set_extra_http_headers({
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
    
    async def search_amazon(self, query: str, limit: int = 10) -> List[Product]:
        """Search Amazon using Playwright"""
        try:
            # Navigate to Amazon search page
            encoded_query = query.replace(' ', '+')
            url = f"https://www.amazon.in/s?k={encoded_query}"
            
            logger.info(f"Searching Amazon for: {query}")
            await self.page.goto(url, wait_until='domcontentloaded', timeout=15000)
            
            # Wait a bit for content to load
            await asyncio.sleep(2)
            
            # Try multiple selectors for product containers
            selectors = [
                '[data-component-type="s-search-result"]',
                '.s-result-item',
                '.sg-col-inner',
                '[data-asin]'
            ]
            
            product_elements = []
            for selector in selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    if elements:
                        product_elements = elements
                        logger.info(f"Found {len(elements)} products using selector: {selector}")
                        break
                except Exception:
                    continue
            
            if not product_elements:
                logger.warning("No product elements found on Amazon")
                return []
            
            # Extract products
            products = []
            for i, element in enumerate(product_elements[:limit]):
                try:
                    product = await self._extract_amazon_product(element)
                    if product and product.name and product.price.current_price > 0:
                        products.append(product)
                except Exception as e:
                    logger.warning(f"Error extracting Amazon product {i}: {e}")
                    continue
            
            logger.info(f"Found {len(products)} valid products on Amazon")
            return products
            
        except Exception as e:
            logger.error(f"Error searching Amazon: {e}")
            return []
    
    async def search_flipkart(self, query: str, limit: int = 10) -> List[Product]:
        """Search Flipkart using Playwright"""
        try:
            # Navigate to Flipkart search page
            encoded_query = query.replace(' ', '%20')
            url = f"https://www.flipkart.com/search?q={encoded_query}"
            
            logger.info(f"Searching Flipkart for: {query}")
            await self.page.goto(url, wait_until='domcontentloaded', timeout=15000)
            
            # Wait a bit for content to load
            await asyncio.sleep(3)
            
            # Try to close any popup/banner that might appear
            try:
                close_button = await self.page.query_selector('button._2KpZ6l')
                if close_button:
                    await close_button.click()
                    await asyncio.sleep(1)
            except:
                pass
            
            # Updated selectors for product containers (not just anchor tags)
            selectors = [
                'div[data-tkid]',  # This is the main product container
                'div._1AtVbE',     # Alternative container
                'div._2kHMtA',     # Another alternative
                'div[class*="_1AtVbE"]',
                'div[class*="_2kHMtA"]',
                'div[class*="product"]'
            ]
            
            product_elements = []
            for selector in selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    if elements:
                        product_elements = elements
                        logger.info(f"Found {len(elements)} products using selector: {selector}")
                        break
                except Exception as e:
                    logger.warning(f"Selector {selector} failed: {e}")
                    continue
            
            if not product_elements:
                logger.warning("No product elements found on Flipkart")
                # Let's try a more generic approach
                try:
                    # Look for any div that contains product links
                    generic_containers = await self.page.query_selector_all('div:has(a[href*="/p/"])')
                    if generic_containers:
                        product_elements = generic_containers
                        logger.info(f"Found {len(generic_containers)} products using generic selector")
                except Exception as e:
                    logger.error(f"Generic selector also failed: {e}")
                    return []
            
            if not product_elements:
                return []
            
            # Extract products
            products = []
            for i, element in enumerate(product_elements[:limit]):
                try:
                    product = await self._extract_flipkart_product(element)
                    if product and product.name and product.price.current_price > 0:
                        products.append(product)
                        logger.info(f"Successfully extracted product {i+1}: {product.name}")
                    else:
                        logger.warning(f"Product {i+1} failed validation: name={product.name if product else 'None'}, price={product.price.current_price if product else 'None'}")
                except Exception as e:
                    logger.warning(f"Error extracting Flipkart product {i}: {e}")
                    continue
            
            logger.info(f"Found {len(products)} valid products on Flipkart")
            return products
            
        except Exception as e:
            logger.error(f"Error searching Flipkart: {e}")
            return []
    
    async def _extract_amazon_product(self, element) -> Optional[Product]:
        """Extract product data from Amazon search result element"""
        try:
            # Extract product name - try multiple selectors
            name_selectors = [
                'h2 a span',
                '.a-size-medium.a-color-base.a-text-normal',
                '.a-size-base-plus.a-color-base.a-text-normal',
                'h2 span'
            ]
            
            name = None
            for selector in name_selectors:
                try:
                    name_element = await element.query_selector(selector)
                    if name_element:
                        name = await name_element.text_content()
                        name = self._clean_text(name) if name else None
                        if name:
                            break
                except Exception:
                    continue
            
            if not name:
                return None
            
            # Extract price - try multiple selectors
            price_selectors = [
                '.a-price-whole',
                '.a-price .a-offscreen',
                '.a-price-current .a-offscreen'
            ]
            
            current_price = None
            for selector in price_selectors:
                try:
                    price_element = await element.query_selector(selector)
                    if price_element:
                        price_text = await price_element.text_content()
                        current_price = self._extract_price(price_text) if price_text else None
                        if current_price:
                            break
                except Exception:
                    continue
            
            # Extract original price
            original_price_selectors = [
                '.a-price.a-text-price .a-offscreen',
                '.a-text-strike'
            ]
            
            original_price = None
            for selector in original_price_selectors:
                try:
                    original_price_element = await element.query_selector(selector)
                    if original_price_element:
                        original_price_text = await original_price_element.text_content()
                        original_price = self._extract_price(original_price_text) if original_price_text else None
                        if original_price:
                            break
                except Exception:
                    continue
            
            # Extract rating
            rating_selectors = [
                '.a-icon-alt',
                '.a-icon-star-small .a-icon-alt'
            ]
            
            rating = None
            for selector in rating_selectors:
                try:
                    rating_element = await element.query_selector(selector)
                    if rating_element:
                        rating_text = await rating_element.text_content()
                        rating = self._extract_rating(rating_text) if rating_text else None
                        if rating:
                            break
                except Exception:
                    continue
            
            # Extract product URL
            url_selectors = [
                'h2 a',
                'a[href*="/dp/"]'
            ]
            
            product_url = ""
            for selector in url_selectors:
                try:
                    url_element = await element.query_selector(selector)
                    if url_element:
                        href = await url_element.get_attribute('href')
                        if href:
                            if href.startswith('/'):
                                product_url = f"https://www.amazon.in{href}"
                            else:
                                product_url = href
                            break
                except Exception:
                    continue
            
            # Extract product ID from URL
            product_id = self._extract_product_id_from_url(product_url)
            
            # Extract image
            img_selectors = [
                'img.s-image',
                'img[data-image-latency]',
                'img'
            ]
            
            images = []
            for selector in img_selectors:
                try:
                    img_element = await element.query_selector(selector)
                    if img_element:
                        src = await img_element.get_attribute('src')
                        alt_text = await img_element.get_attribute('alt') or ''
                        if src and not src.endswith('sprite'):
                            images.append(ProductImage(
                                url=src,
                                alt_text=alt_text,
                                is_primary=True
                            ))
                            break
                except Exception:
                    continue
            
            # Create product objects
            price = ProductPrice(
                current_price=current_price or 0.0,
                original_price=original_price,
                currency="INR"
            )
            
            rating_obj = None
            if rating:
                rating_obj = ProductRating(
                    rating=rating,
                    total_reviews=0
                )
            
            delivery = DeliveryInfo(
                delivery_time="2-5 days",
                free_delivery=True
            )
            
            return Product(
                name=name,
                platform_product_id=product_id,
                platform_url=product_url,
                price=price,
                rating=rating_obj,
                delivery=delivery,
                images=images,
                platform=Platform.AMAZON,
                platform_type=PlatformType.ECOMMERCE
            )
            
        except Exception as e:
            logger.warning(f"Error extracting Amazon product: {e}")
            return None
    
    async def _extract_flipkart_product(self, element) -> Optional[Product]:
        """Extract product data from Flipkart search result element"""
        try:
            # Extract product name - updated selectors
            name_selectors = [
                'div._4rR01T',
                'a._1fQZEK',
                'div[class*="_4rR01T"]',
                'a[title]',
                'div[class*="product"] a',
                'a[href*="/p/"]'
            ]
            
            name = None
            product_link_element = None
            
            for selector in name_selectors:
                try:
                    name_element = await element.query_selector(selector)
                    if name_element:
                        # Try to get text content first
                        name = await name_element.text_content()
                        if not name or name.strip() == "":
                            # Try getting title attribute
                            name = await name_element.get_attribute('title')
                        
                        # Store the link element for URL extraction
                        if 'href' in selector or selector == 'a._1fQZEK':
                            product_link_element = name_element
                        
                        name = self._clean_text(name) if name else None
                        if name and len(name.strip()) > 0:
                            break
                except Exception as e:
                    logger.warning(f"Name selector {selector} failed: {e}")
                    continue
            
            if not name:
                logger.warning("No product name found")
                return None
            
            # Extract price - updated selectors
            price_selectors = [
                'div._30jeq3',
                'div[class*="_30jeq3"]',
                'div._1_WHN1',
                'div[class*="_1_WHN1"]',
                'div._16Jk6d',
                'div[class*="_16Jk6d"]',
                'div[class*="price"]'
            ]
            
            current_price = None
            for selector in price_selectors:
                try:
                    price_element = await element.query_selector(selector)
                    if price_element:
                        price_text = await price_element.text_content()
                        current_price = self._extract_price(price_text) if price_text else None
                        if current_price:
                            break
                except Exception as e:
                    logger.warning(f"Price selector {selector} failed: {e}")
                    continue
            
            if not current_price:
                logger.warning(f"No price found for product: {name}")
                return None
            
            # Extract original price
            original_price_selectors = [
                'div._3I9_wc',
                'div[class*="_3I9_wc"]',
                'div._3_jeJx',
                'div[class*="_3_jeJx"]',
                'span[class*="strike"]'
            ]
            
            original_price = None
            for selector in original_price_selectors:
                try:
                    original_price_element = await element.query_selector(selector)
                    if original_price_element:
                        original_price_text = await original_price_element.text_content()
                        original_price = self._extract_price(original_price_text) if original_price_text else None
                        if original_price:
                            break
                except Exception:
                    continue
            
            # Extract rating
            rating_selectors = [
                'div._3LWZlK',
                'div[class*="_3LWZlK"]',
                'div._2d4LTz',
                'div[class*="_2d4LTz"]',
                'span[class*="rating"]'
            ]
            
            rating = None
            for selector in rating_selectors:
                try:
                    rating_element = await element.query_selector(selector)
                    if rating_element:
                        rating_text = await rating_element.text_content()
                        try:
                            rating = float(rating_text.strip()) if rating_text else None
                            if rating and 0 <= rating <= 5:
                                break
                        except ValueError:
                            continue
                except Exception:
                    continue
            
            # Extract product URL
            product_url = ""
            if product_link_element:
                try:
                    href = await product_link_element.get_attribute('href')
                    if href:
                        if href.startswith('/'):
                            product_url = f"https://www.flipkart.com{href}"
                        else:
                            product_url = href
                except Exception:
                    pass
            
            # If we don't have URL from name element, try other selectors
            if not product_url:
                url_selectors = [
                    'a._1fQZEK',
                    'a[href*="/p/"]'
                ]
                
                for selector in url_selectors:
                    try:
                        url_element = await element.query_selector(selector)
                        if url_element:
                            href = await url_element.get_attribute('href')
                            if href:
                                if href.startswith('/'):
                                    product_url = f"https://www.flipkart.com{href}"
                                else:
                                    product_url = href
                                break
                    except Exception:
                        continue
            
            # Extract product ID
            product_id = self._extract_product_id_from_url(product_url)
            
            # Extract image
            img_selectors = [
                'img._396cs4',
                'img[class*="_396cs4"]',
                'img[src*="image"]',
                'img[data-src]',
                'img'
            ]
            
            images = []
            for selector in img_selectors:
                try:
                    img_element = await element.query_selector(selector)
                    if img_element:
                        src = await img_element.get_attribute('src')
                        if not src:
                            src = await img_element.get_attribute('data-src')
                        if src and not src.endswith('.gif'):  # Avoid loading gifs
                            images.append(ProductImage(
                                url=src,
                                alt_text=name or '',
                                is_primary=True
                            ))
                            break
                except Exception:
                    continue
            
            # Create product objects
            price = ProductPrice(
                current_price=current_price,
                original_price=original_price,
                currency="INR"
            )
            
            rating_obj = None
            if rating:
                rating_obj = ProductRating(
                    rating=rating,
                    total_reviews=0
                )
            
            delivery = DeliveryInfo(
                delivery_time="3-5 days",
                free_delivery=True
            )
            
            product = Product(
                name=name,
                platform_product_id=product_id,
                platform_url=product_url,
                price=price,
                rating=rating_obj,
                delivery=delivery,
                images=images,
                platform=Platform.FLIPKART,
                platform_type=PlatformType.ECOMMERCE
            )
            
            return product
            
        except Exception as e:
            logger.error(f"Error extracting Flipkart product: {e}")
            return None
    
    def _extract_product_id_from_url(self, url: str) -> str:
        """Extract product ID from URL"""
        if not url:
            return "unknown"
        
        # Amazon product ID extraction
        if "amazon.in" in url:
            match = re.search(r'/dp/([A-Z0-9]{10})', url)
            if match:
                return match.group(1)
        
        # Flipkart product ID extraction
        elif "flipkart.com" in url:
            match = re.search(r'/p/([^/?]+)', url)
            if match:
                return match.group(1)
        
        # Fallback: use last part of URL
        return url.split('/')[-1].split('?')[0]
    
    def _extract_price(self, text: str) -> Optional[float]:
        """Extract price from text"""
        if not text:
            return None
        
        # Remove currency symbols and extract numbers
        price_pattern = r'[₹$]?\s*([\d,]+(?:\.\d{2})?)'
        match = re.search(price_pattern, text.replace(',', ''))
        
        if match:
            return float(match.group(1))
        return None
    
    def _extract_rating(self, text: str) -> Optional[float]:
        """Extract rating from text"""
        if not text:
            return None
        
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
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = ' '.join(text.split())
        return text.strip()