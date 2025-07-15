from typing import List, Optional
from bs4 import BeautifulSoup
import re
from urllib.parse import quote_plus
from .base_scraper import BaseScraper
from app.models.product import Product, Platform, PlatformType, ProductPrice, ProductRating, DeliveryInfo, ProductImage, ProductOffer


class BlinkitScraper(BaseScraper):
    """Scraper for Blinkit (Quick Commerce)"""
    
    def get_platform(self) -> Platform:
        return Platform.BLINKIT
    
    def get_platform_type(self) -> PlatformType:
        return PlatformType.QUICK_COMMERCE
    
    def get_base_domain(self) -> str:
        return "blinkit.com"
    
    def get_search_url(self, query: str, **kwargs) -> str:
        """Generate Blinkit search URL with location"""
        encoded_query = quote_plus(query)
        location = kwargs.get('location', 'mumbai')
        return f"https://blinkit.com/search?q={encoded_query}&location={location}"
    
    def parse_search_results(self, html: str, query: str) -> List[Product]:
        """Parse Blinkit search results"""
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        
        # Find product containers (Blinkit specific selectors)
        product_containers = soup.select('.product-card, .ProductCard, [data-testid="product-card"]')
        
        for container in product_containers:
            try:
                product = self._parse_product_container(container)
                if product:
                    products.append(product)
            except Exception as e:
                continue
        
        return products
    
    def _parse_product_container(self, container) -> Optional[Product]:
        """Parse individual product container"""
        try:
            # Extract product ID
            product_id = container.get('data-product-id') or container.get('id', '')
            if not product_id:
                return None
            
            # Extract product name
            name_element = container.select_one('.product-name, .ProductName, h3, h4')
            if not name_element:
                return None
            name = self._clean_text(name_element.get_text())
            
            # Extract price
            price_element = container.select_one('.price, .Price, .product-price')
            current_price = None
            original_price = None
            
            if price_element:
                current_price = self._extract_price(price_element.get_text())
            
            # Check for original price (strikethrough)
            original_price_element = container.select_one('.original-price, .strike-price')
            if original_price_element:
                original_price = self._extract_price(original_price_element.get_text())
            
            if not current_price:
                return None
            
            # Extract image
            img_element = container.select_one('img')
            images = []
            if img_element:
                src = img_element.get('src') or img_element.get('data-src')
                if src:
                    images.append(ProductImage(
                        url=src,
                        alt_text=img_element.get('alt', ''),
                        is_primary=True
                    ))
            
            # Extract product URL
            url_element = container.select_one('a')
            product_url = ""
            if url_element:
                href = url_element.get('href')
                if href:
                    if href.startswith('/'):
                        product_url = f"https://blinkit.com{href}"
                    else:
                        product_url = href
            
            # Create product price object
            price = ProductPrice(
                current_price=current_price,
                original_price=original_price,
                currency="INR"
            )
            
            # Create delivery info (Blinkit is quick commerce)
            delivery = DeliveryInfo(
                delivery_time="10-30 mins",
                free_delivery=True,
                delivery_type="express"
            )
            
            # Create product
            product = Product(
                name=name,
                platform_product_id=product_id,
                platform_url=product_url,
                price=price,
                delivery=delivery,
                images=images
            )
            
            return product
            
        except Exception as e:
            return None
    
    def parse_product_page(self, html: str, product_id: str) -> Optional[Product]:
        """Parse individual product page for detailed information"""
        soup = BeautifulSoup(html, 'html.parser')
        
        try:
            # Extract product name
            name_element = soup.select_one('.product-title, .ProductTitle, h1')
            if not name_element:
                return None
            name = self._clean_text(name_element.get_text())
            
            # Extract price
            price_element = soup.select_one('.current-price, .price-current')
            current_price = None
            if price_element:
                current_price = self._extract_price(price_element.get_text())
            
            if not current_price:
                return None
            
            # Extract original price
            original_price_element = soup.select_one('.original-price, .price-original')
            original_price = None
            if original_price_element:
                original_price = self._extract_price(original_price_element.get_text())
            
            # Extract images
            images = []
            img_elements = soup.select('.product-image img, .ProductImage img')
            for i, img in enumerate(img_elements):
                src = img.get('src') or img.get('data-src')
                if src:
                    images.append(ProductImage(
                        url=src,
                        alt_text=img.get('alt', ''),
                        is_primary=(i == 0)
                    ))
            
            # Extract delivery info
            delivery_text = "10-30 mins"
            free_delivery = True
            
            delivery_element = soup.select_one('.delivery-time, .DeliveryTime')
            if delivery_element:
                delivery_text = self._clean_text(delivery_element.get_text())
            
            # Create product objects
            price = ProductPrice(
                current_price=current_price,
                original_price=original_price,
                currency="INR"
            )
            
            delivery = DeliveryInfo(
                delivery_time=delivery_text,
                free_delivery=free_delivery,
                delivery_type="express"
            )
            
            # Create product
            product = Product(
                name=name,
                platform_product_id=product_id,
                platform_url=f"https://blinkit.com/product/{product_id}",
                price=price,
                delivery=delivery,
                images=images
            )
            
            return product
            
        except Exception as e:
            return None 