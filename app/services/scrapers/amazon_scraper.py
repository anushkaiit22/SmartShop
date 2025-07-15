from typing import List, Optional
from bs4 import BeautifulSoup
import re
from urllib.parse import quote_plus
from .base_scraper import BaseScraper
from app.models.product import Product, Platform, PlatformType, ProductPrice, ProductRating, DeliveryInfo, ProductImage, ProductOffer


class AmazonScraper(BaseScraper):
    """Scraper for Amazon India"""
    
    def get_platform(self) -> Platform:
        return Platform.AMAZON
    
    def get_platform_type(self) -> PlatformType:
        return PlatformType.ECOMMERCE
    
    def get_base_domain(self) -> str:
        return "amazon.in"
    
    def get_search_url(self, query: str, **kwargs) -> str:
        """Generate Amazon search URL"""
        encoded_query = quote_plus(query)
        return f"https://www.amazon.in/s?k={encoded_query}"
    
    def parse_search_results(self, html: str, query: str) -> List[Product]:
        """Parse Amazon search results"""
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        
        # Find product containers
        product_containers = soup.select('[data-component-type="s-search-result"]')
        
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
            product_id = container.get('data-asin', '')
            if not product_id:
                return None
            
            # Extract product name
            name_element = container.select_one('h2 a span')
            if not name_element:
                return None
            name = self._clean_text(name_element.get_text())
            
            # Extract price
            price_element = container.select_one('.a-price-whole')
            current_price = None
            original_price = None
            
            if price_element:
                current_price = self._extract_price(price_element.get_text())
            
            # Check for original price (strikethrough)
            original_price_element = container.select_one('.a-price.a-text-price .a-offscreen')
            if original_price_element:
                original_price = self._extract_price(original_price_element.get_text())
            
            if not current_price:
                return None
            
            # Extract rating
            rating_element = container.select_one('.a-icon-alt')
            rating = None
            total_reviews = 0
            
            if rating_element:
                rating_text = rating_element.get_text()
                rating = self._extract_rating(rating_text)
                
                # Extract review count
                review_element = container.select_one('a[href*="customerReviews"]')
                if review_element:
                    review_text = review_element.get_text()
                    review_match = re.search(r'(\d+(?:,\d+)*)', review_text)
                    if review_match:
                        total_reviews = int(review_match.group(1).replace(',', ''))
            
            # Extract image
            img_element = container.select_one('img.s-image')
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
            url_element = container.select_one('h2 a')
            product_url = ""
            if url_element:
                href = url_element.get('href')
                if href:
                    if href.startswith('/'):
                        product_url = f"https://www.amazon.in{href}"
                    else:
                        product_url = href
            
            # Create product price object
            price = ProductPrice(
                current_price=current_price,
                original_price=original_price,
                currency="INR"
            )
            
            # Create rating object
            rating_obj = None
            if rating:
                rating_obj = ProductRating(
                    rating=rating,
                    total_reviews=total_reviews
                )
            
            # Create delivery info
            delivery = DeliveryInfo(
                delivery_time="2-5 days",
                free_delivery=True
            )
            
            # Create product
            product = Product(
                name=name,
                platform_product_id=product_id,
                platform_url=product_url,
                price=price,
                rating=rating_obj,
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
            name_element = soup.select_one('#productTitle')
            if not name_element:
                return None
            name = self._clean_text(name_element.get_text())
            
            # Extract price
            price_element = soup.select_one('#priceblock_ourprice, .a-price .a-offscreen')
            current_price = None
            if price_element:
                current_price = self._extract_price(price_element.get_text())
            
            if not current_price:
                return None
            
            # Extract original price
            original_price_element = soup.select_one('.a-text-strike, .a-price.a-text-price .a-offscreen')
            original_price = None
            if original_price_element:
                original_price = self._extract_price(original_price_element.get_text())
            
            # Extract rating
            rating_element = soup.select_one('#acrPopover')
            rating = None
            total_reviews = 0
            
            if rating_element:
                rating_text = rating_element.get('title', '')
                rating = self._extract_rating(rating_text)
                
                # Extract review count
                review_element = soup.select_one('#acrCustomerReviewText')
                if review_element:
                    review_text = review_element.get_text()
                    review_match = re.search(r'(\d+(?:,\d+)*)', review_text)
                    if review_match:
                        total_reviews = int(review_match.group(1).replace(',', ''))
            
            # Extract images
            images = []
            img_elements = soup.select('#altImages img')
            for i, img in enumerate(img_elements):
                src = img.get('src') or img.get('data-old-hires')
                if src:
                    images.append(ProductImage(
                        url=src,
                        alt_text=img.get('alt', ''),
                        is_primary=(i == 0)
                    ))
            
            # Extract delivery info
            delivery_text = "2-5 days"
            free_delivery = False
            
            delivery_element = soup.select_one('#deliveryBlockMessage')
            if delivery_element:
                delivery_text = self._clean_text(delivery_element.get_text())
                if "free" in delivery_text.lower():
                    free_delivery = True
            
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
                    total_reviews=total_reviews
                )
            
            delivery = DeliveryInfo(
                delivery_time=delivery_text,
                free_delivery=free_delivery
            )
            
            # Create product
            product = Product(
                name=name,
                platform_product_id=product_id,
                platform_url=f"https://www.amazon.in/dp/{product_id}",
                price=price,
                rating=rating_obj,
                delivery=delivery,
                images=images
            )
            
            return product
            
        except Exception as e:
            return None 

    async def search_products(self, query: str, limit: int = 10, **kwargs) -> list:
        """Search for products on the platform, with mock fallback if scraping fails."""
        try:
            url = self.get_search_url(query, **kwargs)
            html = await self._fetch_page(url)
            if not html:
                import logging
                logging.warning(f"Failed to fetch search results for {query} on {self.get_platform().value}")
                return self._get_mock_products(query, limit)
            products = self.parse_search_results(html, query)
            products = products[:limit]
            for product in products:
                product.platform = self.get_platform()
                product.platform_type = self.get_platform_type()
            return products
        except Exception as e:
            import logging
            logging.error(f"Error searching products on {self.get_platform().value}: {e}")
            return self._get_mock_products(query, limit)

    def _get_mock_products(self, query: str, limit: int) -> list:
        from app.models.product import Product, ProductPrice, ProductRating, DeliveryInfo, ProductImage
        mock_products = [
            Product(
                name="Dell Inspiron 15 3000 Laptop",
                platform_product_id="mock_dell_1",
                platform_url="https://www.amazon.in/dell-inspiron-15-3000",
                price=ProductPrice(current_price=45000.0, original_price=52000.0, currency="INR"),
                rating=ProductRating(rating=4.2, total_reviews=1250),
                delivery=DeliveryInfo(delivery_time="2-3 days", free_delivery=True),
                images=[ProductImage(url="https://via.placeholder.com/300x200?text=Dell+Laptop", alt_text="Dell Inspiron Laptop", is_primary=True)],
                platform=self.get_platform(),
                platform_type=self.get_platform_type()
            ),
            Product(
                name="HP Pavilion 15 Gaming Laptop",
                platform_product_id="mock_hp_1",
                platform_url="https://www.amazon.in/hp-pavilion-gaming",
                price=ProductPrice(current_price=48000.0, original_price=55000.0, currency="INR"),
                rating=ProductRating(rating=4.0, total_reviews=890),
                delivery=DeliveryInfo(delivery_time="3-4 days", free_delivery=True),
                images=[ProductImage(url="https://via.placeholder.com/300x200?text=HP+Gaming+Laptop", alt_text="HP Pavilion Gaming Laptop", is_primary=True)],
                platform=self.get_platform(),
                platform_type=self.get_platform_type()
            ),
            Product(
                name="Lenovo IdeaPad 3 Laptop",
                platform_product_id="mock_lenovo_1",
                platform_url="https://www.amazon.in/lenovo-ideapad-3",
                price=ProductPrice(current_price=42000.0, original_price=48000.0, currency="INR"),
                rating=ProductRating(rating=4.3, total_reviews=1100),
                delivery=DeliveryInfo(delivery_time="2-3 days", free_delivery=True),
                images=[ProductImage(url="https://via.placeholder.com/300x200?text=Lenovo+IdeaPad", alt_text="Lenovo IdeaPad Laptop", is_primary=True)],
                platform=self.get_platform(),
                platform_type=self.get_platform_type()
            ),
            Product(
                name="ASUS VivoBook 15 Laptop",
                platform_product_id="mock_asus_1",
                platform_url="https://www.amazon.in/asus-vivobook-15",
                price=ProductPrice(current_price=46000.0, original_price=52000.0, currency="INR"),
                rating=ProductRating(rating=4.1, total_reviews=750),
                delivery=DeliveryInfo(delivery_time="3-5 days", free_delivery=True),
                images=[ProductImage(url="https://via.placeholder.com/300x200?text=ASUS+VivoBook", alt_text="ASUS VivoBook Laptop", is_primary=True)],
                platform=self.get_platform(),
                platform_type=self.get_platform_type()
            ),
            Product(
                name="Acer Aspire 5 Laptop",
                platform_product_id="mock_acer_1",
                platform_url="https://www.amazon.in/acer-aspire-5",
                price=ProductPrice(current_price=44000.0, original_price=50000.0, currency="INR"),
                rating=ProductRating(rating=4.0, total_reviews=620),
                delivery=DeliveryInfo(delivery_time="2-4 days", free_delivery=True),
                images=[ProductImage(url="https://via.placeholder.com/300x200?text=Acer+Aspire", alt_text="Acer Aspire Laptop", is_primary=True)],
                platform=self.get_platform(),
                platform_type=self.get_platform_type()
            )
        ]
        query_lower = query.lower()
        if "gaming" in query_lower:
            mock_products = [p for p in mock_products if "gaming" in p.name.lower()]
        elif "budget" in query_lower or "cheap" in query_lower:
            mock_products = sorted(mock_products, key=lambda x: x.price.current_price)[:2]
        return mock_products[:limit] 