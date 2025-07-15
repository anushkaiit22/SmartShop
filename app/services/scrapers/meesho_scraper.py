import re
import random
import sys
import asyncio
from typing import List, Optional
from bs4 import BeautifulSoup
from app.services.scrapers.base_scraper import BaseScraper
from app.models.product import Product, Platform, PlatformType, ProductPrice, ProductRating, DeliveryInfo

class MeeshoScraper(BaseScraper):
    def get_platform(self) -> Platform:
        return Platform.MEESHO

    def get_platform_type(self) -> PlatformType:
        return PlatformType.ECOMMERCE

    def get_search_url(self, query: str, **kwargs) -> str:
        return f"https://www.meesho.com/search?q={query.replace(' ', '%20')}"

    async def _fetch_page(self, url: str) -> Optional[str]:
        """Override fetch page with Meesho-specific headers"""
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        # Meesho-specific headers to avoid detection
        meesho_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.meesho.com/',
            'Origin': 'https://www.meesho.com'
        }
        
        # Rotate user agents
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        for attempt in range(3):
            try:
                # Update headers for each attempt
                meesho_headers['User-Agent'] = random.choice(user_agents)
                
                async with self.session.get(url, headers=meesho_headers) as response:
                    if response.status == 200:
                        content = await response.text()
                        if len(content) > 1000:  # Basic check for valid content
                            return content
                        else:
                            print(f"Received suspiciously small content ({len(content)} chars) from {url}", file=sys.stderr)
                    elif response.status == 403:
                        print(f"HTTP 403 (Forbidden) on attempt {attempt + 1} for {url} - likely anti-bot protection", file=sys.stderr)
                        if attempt == 2:  # Last attempt
                            print(f"Failed to access {url} after 3 attempts - Meesho is blocking the scraper", file=sys.stderr)
                    elif response.status == 429:  # Rate limited
                        wait_time = int(response.headers.get('Retry-After', 60))
                        print(f"Rate limited, waiting {wait_time} seconds", file=sys.stderr)
                        await asyncio.sleep(wait_time)
                    else:
                        print(f"HTTP {response.status} for {url}", file=sys.stderr)
                        
            except Exception as e:
                print(f"Error fetching {url}: {e}", file=sys.stderr)
        
        return None

    def parse_search_results(self, html: str, query: str) -> List[Product]:
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        
        # Try multiple selectors for Meesho product cards
        selectors = [
            'div[class*="ProductList__GridCol"] a',
            'div[class*="ProductCard"] a',
            'div[class*="product-card"] a',
            'a[href*="/product/"]',
            'div[data-testid*="product"] a'
        ]
        
        cards = []
        for selector in selectors:
            cards = soup.select(selector)
            if cards:
                print(f"Found {len(cards)} product cards with selector: {selector}", file=sys.stderr)
                break
        
        if not cards:
            print("No product cards found on Meesho page", file=sys.stderr)
            return []
        
        for card in cards[:10]:  # Limit to first 10 products
            try:
                # Extract URL
                url = card.get('href')
                if not url:
                    continue
                url = f"https://www.meesho.com{url}" if url.startswith('/') else url
                
                # Extract product name
                name = None
                name_selectors = [
                    'p[class*="Text__StyledText"]',
                    'h3[class*="Text__StyledText"]',
                    'div[class*="ProductCard__Title"]',
                    'span[class*="ProductCard__Title"]',
                    'h3', 'h4', 'p'
                ]
                
                for selector in name_selectors:
                    name_el = card.select_one(selector)
                    if name_el:
                        name = self._clean_text(name_el.text)
                        if name and len(name) > 5:  # Basic validation
                            break
                
                # Extract price
                price = None
                price_selectors = [
                    'h5[class*="Text__StyledText"]',
                    'span[class*="ProductCard__Price"]',
                    'div[class*="ProductCard__Price"]',
                    'span[class*="price"]',
                    'h5', 'h4'
                ]
                
                for selector in price_selectors:
                    price_el = card.select_one(selector)
                    if price_el:
                        price = self._extract_price(price_el.text)
                        if price:
                            break
                
                # Extract rating
                rating = None
                rating_selectors = [
                    'span[class*="Rating__StyledRating"]',
                    'div[class*="Rating"]',
                    'span[class*="rating"]'
                ]
                
                for selector in rating_selectors:
                    rating_el = card.select_one(selector)
                    if rating_el:
                        rating = self._extract_rating(rating_el.text)
                        if rating:
                            break
                
                # Create product if we have essential data
                if name and price and url:
                    product = Product(
                        id=None,
                        name=name,
                        description=None,
                        brand=None,
                        category=None,
                        subcategory=None,
                        platform=Platform.MEESHO,
                        platform_type=PlatformType.ECOMMERCE,
                        platform_product_id=None,
                        platform_url=url,
                        price=ProductPrice(current_price=price),
                        images=[],
                        rating=ProductRating(rating=rating, total_reviews=0) if rating else None,
                        delivery=DeliveryInfo(delivery_time="2-7 days"),
                        specifications={},
                        availability=True,
                        in_stock=True,
                        stock_quantity=None
                    )
                    products.append(product)
                    print(f"Found Meesho product: {name[:50]}... - ₹{price}", file=sys.stderr)
                else:
                    print(f"Meesho product missing data: name={bool(name)}, price={bool(price)}, url={bool(url)}", file=sys.stderr)
                    
            except Exception as e:
                print(f"Error processing Meesho product: {e}", file=sys.stderr)
                continue
        
        print(f"Meesho search completed. Found {len(products)} valid products", file=sys.stderr)
        return products

    def parse_product_page(self, html: str, product_id: str) -> Optional[Product]:
        # Not implemented for now
        return None

    def get_base_domain(self) -> str:
        return "https://www.meesho.com" 