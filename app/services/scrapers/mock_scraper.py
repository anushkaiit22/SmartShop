import random
from typing import List, Optional
from datetime import datetime
from app.services.scrapers.base_scraper import BaseScraper
from app.models.product import Product, Platform, PlatformType, ProductPrice, ProductRating, DeliveryInfo

class MockScraper(BaseScraper):
    """Mock scraper that returns realistic product data for demo purposes"""
    
    def __init__(self, platform: Platform):
        self.mock_platform = platform
        super().__init__()
    
    def get_platform(self) -> Platform:
        return self.mock_platform
    
    def get_platform_type(self) -> PlatformType:
        if self.mock_platform in [Platform.BLINKIT, Platform.ZEPTO, Platform.INSTAMART]:
            return PlatformType.QUICK_COMMERCE
        return PlatformType.ECOMMERCE
    
    def get_search_url(self, query: str, **kwargs) -> str:
        return f"https://mock-{self.mock_platform.value}.com/search?q={query}"
    
    async def _fetch_page(self, url: str) -> Optional[str]:
        """Override to return mock HTML instead of making HTTP requests"""
        # Return a simple mock HTML that will be parsed
        return f"<html><body><div>Mock {self.mock_platform.value} page for demo</div></body></html>"
    
    def parse_search_results(self, html: str, query: str) -> List[Product]:
        """Generate realistic mock products"""
        products = []
        
        # Mock product data based on platform
        if self.mock_platform in [Platform.AMAZON, Platform.MEESHO]:
            # Generate mock products based on the query
            mock_products = [
                (f"{query.title()} {i+1}", random.randint(299, 4999), round(random.uniform(3.8, 4.8), 1))
                for i in range(5)
            ]
        elif self.mock_platform == Platform.BLINKIT:
            mock_products = [
                ("Amul Full Cream Milk 1L", 58, 4.4),
                ("Britannia Brown Bread", 35, 4.2),
                ("Nestle Maggi Noodles", 14, 4.0),
                ("Coca Cola 2L Bottle", 95, 4.1),
                ("Lay's Classic Chips", 20, 4.3)
            ]
        else:
            mock_products = [
                ("Generic Product 1", 1000, 4.0),
                ("Generic Product 2", 1500, 4.1),
                ("Generic Product 3", 2000, 4.2),
                ("Generic Product 4", 2500, 4.3),
                ("Generic Product 5", 3000, 4.4)
            ]
        
        for i, (name, price, rating) in enumerate(mock_products):
            # Add query to product name for realism
            product_name = f"{name} - {query.title()}"
            
            # Generate realistic URL
            product_url = f"https://www.{self.mock_platform.value}.com/product/{i+1}/{product_name.lower().replace(' ', '-')}"
            
            # Determine delivery time based on platform type
            if self.get_platform_type() == PlatformType.QUICK_COMMERCE:
                delivery_time = "10-30 mins"
            else:
                delivery_time = "2-5 days"
            
            product = Product(
                id=f"mock_{self.mock_platform.value}_{i+1}",
                name=product_name,
                description=f"High-quality {query} from {self.mock_platform.value.title()}",
                brand="Demo Brand",
                category=query,
                subcategory=None,
                platform=self.mock_platform,
                platform_type=self.get_platform_type(),
                platform_product_id=f"mock_{i+1}",
                platform_url=product_url,
                price=ProductPrice(
                    current_price=price,
                    original_price=price * 1.2,  # 20% markup
                    currency="INR"
                ),
                images=[],
                rating=ProductRating(rating=rating, total_reviews=random.randint(50, 500)),
                delivery=DeliveryInfo(
                    delivery_time=delivery_time,
                    delivery_fee=0 if price > 500 else 40,
                    free_delivery=price > 500
                ),
                specifications={},
                availability=True,
                in_stock=True,
                stock_quantity=random.randint(10, 100)
            )
            products.append(product)
        
        return products
    
    def parse_product_page(self, html: str, product_id: str) -> Optional[Product]:
        # Return a mock product for individual product pages
        return None
    
    def get_base_domain(self) -> str:
        return f"https://www.{self.mock_platform.value}.com"

class MockAmazonScraper(MockScraper):
    def __init__(self):
        super().__init__(Platform.AMAZON)

class MockMeeshoScraper(MockScraper):
    def __init__(self):
        super().__init__(Platform.MEESHO)

class MockBlinkitScraper(MockScraper):
    def __init__(self):
        super().__init__(Platform.BLINKIT) 