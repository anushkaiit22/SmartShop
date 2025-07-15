from typing import List, Optional, Dict, Any
import re
from bs4 import BeautifulSoup
from app.services.scrapers.base_scraper import BaseScraper
from app.models.product import Product, Platform, PlatformType, ProductPrice, ProductRating, DeliveryInfo, ProductImage, ProductOffer


class FlipkartScraper(BaseScraper):
    """Scraper for Flipkart e-commerce platform"""
    
    def get_platform(self) -> Platform:
        return Platform.FLIPKART
    
    def get_platform_type(self) -> PlatformType:
        return PlatformType.ECOMMERCE
    
    def get_base_domain(self) -> str:
        """Return the base domain for Flipkart"""
        return "flipkart.com"
    
    def get_search_url(self, query: str, **kwargs) -> str:
        """Generate Flipkart search URL"""
        # Clean and encode query
        clean_query = query.replace(' ', '%20')
        return f"https://www.flipkart.com/search?q={clean_query}"
    
    def parse_search_results(self, html: str, query: str) -> List[Product]:
        """Parse Flipkart search results"""
        products = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Updated selectors for Flipkart's current structure
        # Try multiple selectors for product containers
        product_containers = []
        
        # Try different container selectors
        selectors = [
            'div[data-id]',  # Current selector from your playwright scraper
            'div[data-tkid]',  # Your original selector
            'div._1AtVbE',  # Common Flipkart product container
            'div._13oc-S',  # Another common container
            'div.s1Q9rs',   # Alternative container
            'div._2kHMtA',  # Grid view container
            'div.bhgxx2'    # List view container
        ]
        
        for selector in selectors:
            containers = soup.select(selector)
            if containers:
                product_containers = containers
                print(f"Found {len(containers)} products using selector: {selector}")
                break
        
        if not product_containers:
            print("No product containers found with any selector")
            return products
        
        for container in product_containers[:10]:  # Limit to 10 results
            try:
                product = self._parse_product_container(container, query)
                if product:
                    products.append(product)
            except Exception as e:
                print(f"Error parsing product container: {e}")
                continue
        
        return products
    
    def _parse_product_container(self, container, query: str) -> Optional[Product]:
        """Parse individual product container from search results"""
        try:
            # Extract product name with multiple fallback selectors
            name = self._extract_product_name(container)
            if not name:
                print(f"No product name found in container")
                return None
            
            # Extract price with multiple fallback selectors
            current_price, original_price = self._extract_prices(container)
            if current_price == 0:
                print(f"No price found for product: {name}")
                return None
            
            # Extract rating
            rating, rating_count = self._extract_rating(container)
            
            # Extract product URL and ID
            product_url, product_id = self._extract_product_url(container)
            if not product_url:
                print(f"No product URL found for: {name}")
                return None
            
            # Extract image
            image_url = self._extract_image_url(container)
            
            # Default delivery info for search results
            delivery_time = "3-5 days"
            
            return Product(
                name=name,
                platform=Platform.FLIPKART,
                platform_type=PlatformType.ECOMMERCE,
                platform_product_id=product_id,
                platform_url=product_url,
                price=ProductPrice(
                    current_price=current_price,
                    original_price=original_price,
                    currency="INR"
                ),
                rating=ProductRating(
                    rating=rating,
                    total_ratings=rating_count
                ) if rating else None,
                images=[ProductImage(url=image_url)] if image_url else [],
                delivery=DeliveryInfo(
                    delivery_time=delivery_time,
                    delivery_cost=0.0,
                    is_free_delivery=True
                )
            )
            
        except Exception as e:
            print(f"Error parsing product container: {e}")
            return None
    
    def _extract_product_name(self, container) -> str:
        """Extract product name with multiple fallback selectors"""
        name_selectors = [
            'div.KzDlHZ',      # Current Flipkart product name
            'div._4rR01T',     # Original selector
            'a.s1Q9rs',        # Link text
            'div.IRpwTa',      # Alternative
            'div._2WkVRV',     # Another alternative
            'div.col-7-12',    # Column-based layout
            'a[title]',        # Link with title attribute
            'div[title]',      # Div with title attribute
            'span.B_NuCI',     # Product page selector
        ]
        
        for selector in name_selectors:
            element = container.select_one(selector)
            if element:
                name = self._extract_text(element)
                if name and len(name.strip()) > 3:  # Ensure meaningful name
                    return name
        
        # If no specific selector works, try to find any text that looks like a product name
        all_text = container.get_text(strip=True)
        if all_text and len(all_text) > 10:
            # Look for product-like text patterns
            lines = all_text.split('\n')
            for line in lines:
                if len(line.strip()) > 10 and not line.strip().startswith('₹'):
                    return line.strip()
        
        return ""
    
    def _extract_prices(self, container) -> tuple[float, float]:
        """Extract current and original prices"""
        current_price = 0.0
        original_price = 0.0
        
        # Current price selectors
        current_price_selectors = [
            'div._30jeq3',      # Original selector
            'div._1_WHN1',      # Alternative
            'div._3tbKJL',      # Another alternative
            'div.Nx9bqj',       # Current price class
            'div._25b18c',      # Price display
            'span._2-_8nC',     # Price span
            'div._1vC4OE',      # Price container
        ]
        
        # Original price selectors
        original_price_selectors = [
            'div._3I9_wc',      # Original selector
            'div._27UcVY',      # Alternative
            'div._3auQ3N',      # Strikethrough price
            'span._2Tpdn3',     # Original price span
            'div._25b18c',      # Generic price
        ]
        
        # Extract current price
        for selector in current_price_selectors:
            element = container.select_one(selector)
            if element:
                price_text = self._extract_text(element)
                if price_text and '₹' in price_text:
                    current_price = self._extract_price(price_text)
                    if current_price > 0:
                        break
        
        # Extract original price
        for selector in original_price_selectors:
            element = container.select_one(selector)
            if element:
                price_text = self._extract_text(element)
                if price_text and '₹' in price_text:
                    original_price = self._extract_price(price_text)
                    if original_price > 0:
                        break
        
        # If no prices found, try to extract from all text
        if current_price == 0:
            all_text = container.get_text()
            price_matches = re.findall(r'₹([\d,]+)', all_text)
            if price_matches:
                prices = [self._extract_price(f"₹{match}") for match in price_matches]
                prices = [p for p in prices if p > 0]
                if prices:
                    current_price = min(prices)  # Usually the first/lowest price is current
                    if len(prices) > 1:
                        original_price = max(prices)  # Higher price is usually original
        
        return current_price, original_price
    
    def _extract_rating(self, container) -> tuple[Optional[float], int]:
        """Extract rating and rating count"""
        rating = None
        rating_count = 0
        
        # Rating selectors
        rating_selectors = [
            'div._3LWZlK',      # Original selector
            'div._3n8db4',      # Alternative rating
            'span._2_R_DZ',     # Rating span
            'div.gUuXy-',       # Rating container
        ]
        
        for selector in rating_selectors:
            element = container.select_one(selector)
            if element:
                rating_text = self._extract_text(element)
                try:
                    rating = float(rating_text)
                    break
                except ValueError:
                    continue
        
        # Rating count selectors
        rating_count_selectors = [
            'span._2_R_DZ',     # Original selector
            'span._13vcmD',     # Alternative
            'div._2d4LTz',      # Rating count container
        ]
        
        for selector in rating_count_selectors:
            element = container.select_one(selector)
            if element:
                count_text = self._extract_text(element)
                rating_count = self._extract_number(count_text)
                if rating_count > 0:
                    break
        
        return rating, rating_count
    
    def _extract_product_url(self, container) -> tuple[str, str]:
        """Extract product URL and ID"""
        url_selectors = [
            'a._1fQZEK',        # Original selector
            'a.s1Q9rs',         # Alternative
            'a.IRpwTa',         # Another alternative
            'a._2UzuFa',        # Link class
            'a[href*="/p/"]',   # Any link containing /p/
            'a[href*="pid="]',  # Any link containing pid=
        ]
        
        for selector in url_selectors:
            element = container.select_one(selector)
            if element and element.get('href'):
                href = element.get('href')
                if href.startswith('/'):
                    product_url = "https://www.flipkart.com" + href
                else:
                    product_url = href
                
                product_id = self._extract_product_id(product_url)
                return product_url, product_id
        
        return "", ""
    
    def _extract_image_url(self, container) -> str:
        """Extract product image URL"""
        image_selectors = [
            'img._396cs4',      # Original selector
            'img._2r_T1I',      # Alternative
            'img._3dqZjq',      # Another alternative
            'img[src*="rukminim"]',  # Flipkart image CDN
            'img[src*="img"]',  # Generic image
        ]
        
        for selector in image_selectors:
            element = container.select_one(selector)
            if element and element.get('src'):
                return element.get('src')
        
        return ""
    
    def parse_product_page(self, html: str, product_id: str) -> Optional[Product]:
        """Parse individual Flipkart product page"""
        soup = BeautifulSoup(html, 'html.parser')
        
        try:
            # Extract product details
            name = self._extract_text(soup.find('span', {'class': 'B_NuCI'}))
            if not name:
                # Try alternative selectors for product name
                name_selectors = ['h1.yhB1nd', 'span.B_NuCI', 'div.KzDlHZ']
                for selector in name_selectors:
                    element = soup.select_one(selector)
                    if element:
                        name = self._extract_text(element)
                        break
            
            if not name:
                return None
            
            # Price extraction with multiple selectors
            current_price, original_price = self._extract_prices(soup)
            
            # Rating
            rating_elem = soup.find('div', {'class': '_3LWZlK'})
            rating = float(rating_elem.text) if rating_elem else None
            
            rating_count_elem = soup.find('span', {'class': '_2_R_DZ'})
            rating_count = self._extract_number(rating_count_elem.text if rating_count_elem else "0")
            
            # Images
            image_elem = soup.find('img', {'class': '_396cs4'})
            image_url = image_elem.get('src') if image_elem else None
            
            # Delivery info
            delivery_elem = soup.find('div', {'class': '_2Tpdn3'})
            delivery_time = self._extract_delivery_time(delivery_elem.text if delivery_elem else "3-5 days")
            
            return Product(
                name=name,
                platform=Platform.FLIPKART,
                platform_type=PlatformType.ECOMMERCE,
                platform_product_id=product_id,
                platform_url=f"https://www.flipkart.com/product/{product_id}",
                price=ProductPrice(
                    current_price=current_price,
                    original_price=original_price,
                    currency="INR"
                ),
                rating=ProductRating(
                    rating=rating,
                    total_ratings=rating_count
                ) if rating else None,
                images=[ProductImage(url=image_url)] if image_url else [],
                delivery=DeliveryInfo(
                    delivery_time=delivery_time,
                    delivery_cost=0.0,
                    is_free_delivery=True
                )
            )
            
        except Exception as e:
            print(f"Error parsing product page: {e}")
            return None
    
    def _extract_text(self, element) -> str:
        """Extract text from element"""
        if not element:
            return ""
        return element.get_text(strip=True)
    
    def _extract_price(self, price_text: str) -> float:
        """Extract price from text"""
        if not price_text:
            return 0.0
        # Remove currency symbols and commas, keep only digits and decimal points
        price = re.sub(r'[^\d.]', '', price_text.replace(',', ''))
        try:
            return float(price)
        except ValueError:
            return 0.0
    
    def _extract_number(self, text: str) -> int:
        """Extract number from text"""
        if not text:
            return 0
        # Extract numbers only, handle comma separators
        text = text.replace(',', '')
        numbers = re.findall(r'\d+', text)
        if numbers:
            return int(numbers[0])
        return 0
    
    def _extract_product_id(self, url: str) -> str:
        """Extract product ID from URL"""
        # Extract product ID from Flipkart URL
        # Try multiple patterns
        patterns = [
            r'/p/([^/?]+)',     # /p/product-id
            r'pid=([^&]+)',     # pid=product-id
            r'/([^/]+)/p/',     # /product-name/p/
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # Fallback to last part of URL
        return url.split('/')[-1].split('?')[0]
    
    def _extract_delivery_time(self, delivery_text: str) -> str:
        """Extract delivery time from text"""
        if not delivery_text:
            return "3-5 days"
        
        # Look for patterns like "2-3 days", "Next day", etc.
        time_patterns = [
            r'(\d+-\d+\s*days?)',
            r'(\d+\s*days?)',
            r'(next\s*day)',
            r'(same\s*day)',
            r'(tomorrow)',
            r'(today)'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, delivery_text.lower())
            if match:
                return match.group(1)
        
        return "3-5 days"