from openai import OpenAI
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import json
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

# Configure OpenAI client
client = None
if settings.OPENAI_API_KEY:
    client = OpenAI(api_key=settings.OPENAI_API_KEY)


class ProductIntent(BaseModel):
    """Model for parsed product intent"""
    product_name: str
    quantity: int = 1
    category: Optional[str] = None
    brand: Optional[str] = None
    max_price: Optional[float] = None
    min_rating: Optional[float] = None
    specifications: Dict[str, Any] = {}


class QueryConstraints(BaseModel):
    """Model for query constraints"""
    total_budget: Optional[float] = None
    delivery_preference: Optional[str] = None  # "fast", "cheap", "balanced"
    preferred_platforms: List[str] = []
    location: Optional[str] = None


class ParsedQuery(BaseModel):
    """Model for parsed shopping query"""
    products: List[ProductIntent]
    constraints: QueryConstraints
    original_query: str
    confidence_score: float


class QueryParser:
    """Service for parsing natural language shopping queries"""
    
    def __init__(self):
        self.system_prompt = """
        You are a friendly, interactive shopping robot assistant. Your job is to help users add products to their cart or search for products across multiple e-commerce platforms.
        
        IMPORTANT RULES:
        - ALWAYS extract product information if the user mentions ANY product, even if it's not in a predefined category
        - If the user mentions ANY item they want to buy/get/add, treat it as a product request
        - Only ask for confirmation if the user's message is completely vague like "add something" or "buy anything"
        - Extract descriptive phrases as complete product names (e.g., "black sock", "red shirt", "gaming laptop")
        - Always be helpful and extract what the user actually wants
        
        Return a JSON object with the following structure:
        {
            "products": [
                {
                    "product_name": "string",
                    "quantity": number,
                    "category": "string (optional)",
                    "brand": "string (optional)",
                    "color": "string (optional)", 
                    "size": "string (optional)",
                    "max_price": number (optional),
                    "min_rating": number (optional),
                    "specifications": {}
                }
            ],
            "constraints": {
                "total_budget": number (optional),
                "delivery_preference": "fast|cheap|balanced (optional)",
                "preferred_platforms": ["string"] (optional),
                "location": "string (optional)"
            }
        }
        
        Examples:
        - "black sock" → Extract product_name: "black sock"
        - "can i get a black sock" → Extract product_name: "black sock"
        - "I need 2 kg rice and a laptop under 50000" → Extract rice (2kg) and laptop (max 50000)
        - "Buy milk, bread, and a smartphone with 4+ rating" → Extract items with rating constraint
        - "white kurti extra small" → Extract product_name: "white kurti", size: "extra small"
        - "Add a blue t-shirt, size L, under 500" → Extract product_name: "blue t-shirt", size: "L", max_price: 500
        - "laptop under 50k" → Extract product_name: "laptop", max_price: 50000
        - "phone with at least 4 star rating" → Extract product_name: "phone", min_rating: 4
        - "gaming mouse" → Extract product_name: "gaming mouse"
        - "red running shoes" → Extract product_name: "red running shoes"
        """
    
    async def parse_query(self, query: str) -> ParsedQuery:
        """Parse natural language shopping query"""
        try:
            if not client:
                # Fallback to simple parsing if OpenAI is not configured
                return self._simple_parse(query)

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Parse this shopping query: {query}"}
                ],
                temperature=0.1,
                max_tokens=500
            )

            content = response.choices[0].message.content
            try:
                parsed_data = json.loads(content)
            except Exception as e:
                logger.error(f"OpenAI response not valid JSON: {content}")
                return self._simple_parse(query)
                
            if not parsed_data or not isinstance(parsed_data, dict):
                logger.error(f"OpenAI response is empty or not a dict: {content}")
                return self._simple_parse(query)

            # Convert to Pydantic models
            products = [ProductIntent(**product) for product in parsed_data.get("products", [])]
            constraints = QueryConstraints(**parsed_data.get("constraints", {}))

            return ParsedQuery(
                products=products,
                constraints=constraints,
                original_query=query,
                confidence_score=0.9
            )

        except Exception as e:
            logger.error(f"Error parsing query: {e}")
            # Fallback to simple parsing
            return self._simple_parse(query)
    
    def _simple_parse(self, query: str) -> ParsedQuery:
        """Enhanced fallback parser that handles any product mention"""
        query_lower = query.lower().strip()
        products = []

        # Skip empty queries or very generic requests
        if not query_lower or query_lower in ["hi", "hello", "hey", "add something", "buy anything", "get me something"]:
            return ParsedQuery(
                products=[],
                constraints=QueryConstraints(),
                original_query=query,
                confidence_score=0.3
            )

        # Extract products using multiple strategies
        products.extend(self._extract_known_products(query_lower))
        
        # If no known products found, try to extract any product-like phrases
        if not products:
            products.extend(self._extract_generic_products(query, query_lower))

        # Extract constraints
        constraints = self._extract_constraints(query_lower)

        return ParsedQuery(
            products=products,
            constraints=constraints,
            original_query=query,
            confidence_score=0.7 if products else 0.3
        )
    
    def _extract_known_products(self, query_lower: str) -> List[ProductIntent]:
        """Extract known product categories"""
        products = []
        
        # Common grocery items
        grocery_items = ["milk", "bread", "rice", "sugar", "salt", "oil", "flour", "eggs", "butter", "tea", "coffee"]
        for item in grocery_items:
            if item in query_lower:
                quantity = self._extract_quantity(query_lower, item)
                products.append(ProductIntent(
                    product_name=item,
                    quantity=quantity,
                    category="grocery"
                ))

        # Electronics
        electronics = ["laptop", "phone", "smartphone", "headphones", "charger", "cable", "mouse", "keyboard", "monitor", "tablet"]
        for item in electronics:
            if item in query_lower:
                products.append(ProductIntent(
                    product_name=item,
                    quantity=1,
                    category="electronics"
                ))

        # Clothing items (expanded list)
        clothing_items = [
            "kurti", "shirt", "t-shirt", "tshirt", "dress", "jeans", "pant", "pants", "trouser", "trousers",
            "skirt", "top", "saree", "blouse", "jacket", "coat", "sweater", "hoodie", "sock", "socks",
            "shoe", "shoes", "sandal", "sandals", "sneaker", "sneakers", "boot", "boots", "cap", "hat"
        ]
        
        for item in clothing_items:
            if item in query_lower:
                # Extract full product name with descriptors
                full_product_name = self._extract_full_product_name(query_lower, item)
                products.append(ProductIntent(
                    product_name=full_product_name,
                    quantity=1,
                    category="clothing"
                ))
                break  # Only extract one clothing item to avoid duplicates

        return products
    
    def _extract_generic_products(self, original_query: str, query_lower: str) -> List[ProductIntent]:
        """Extract any product-like phrases from the query"""
        products = []
        
        # Look for common product request patterns
        import re
        
        # Patterns like "get a X", "buy X", "I want X", "add X", "X please"
        patterns = [
            r"(?:get|buy|add|want|need|looking for|search for|find)\s+(?:a|an|some|the)?\s*([a-zA-Z0-9\s]+?)(?:\s+(?:please|to cart|in cart))?$",
            r"(?:can i get|could i get|i need|i want)\s+(?:a|an|some|the)?\s*([a-zA-Z0-9\s]+?)(?:\s+(?:please|to cart|in cart))?$",
            r"^([a-zA-Z0-9\s]+?)(?:\s+(?:please|to cart|in cart))?$"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query_lower, re.IGNORECASE)
            if match:
                product_phrase = match.group(1).strip()
                
                # Filter out very generic words
                if product_phrase and len(product_phrase) > 2 and product_phrase not in ["something", "anything", "item", "product"]:
                    # Use original casing for product name
                    original_match = re.search(pattern, original_query, re.IGNORECASE)
                    if original_match:
                        original_product = original_match.group(1).strip()
                        products.append(ProductIntent(
                            product_name=original_product,
                            quantity=1,
                            category="general"
                        ))
                    break
        
        return products
    
    def _extract_full_product_name(self, query_lower: str, base_item: str) -> str:
        """Extract full product name with color, size, brand etc."""
        import re
        
        # Colors
        colors = ["white", "black", "red", "blue", "green", "yellow", "pink", "orange", "purple", "grey", "gray", "brown", "beige", "navy", "maroon"]
        
        # Find color + item combinations
        for color in colors:
            if f"{color} {base_item}" in query_lower:
                return f"{color} {base_item}"
        
        # Check for adjectives before the item
        adjective_pattern = rf"(\w+)\s+{base_item}"
        match = re.search(adjective_pattern, query_lower)
        if match:
            adjective = match.group(1)
            if adjective not in ["a", "an", "the", "some", "get", "buy", "add", "want", "need"]:
                return f"{adjective} {base_item}"
        
        return base_item
    
    def _extract_constraints(self, query_lower: str) -> QueryConstraints:
        """Extract budget and other constraints"""
        budget = self._extract_budget(query_lower)
        
        delivery_pref = None
        if any(word in query_lower for word in ["fast", "quick", "urgent", "immediate"]):
            delivery_pref = "fast"
        elif any(word in query_lower for word in ["cheap", "economical", "budget"]):
            delivery_pref = "cheap"
        
        return QueryConstraints(
            total_budget=budget,
            delivery_preference=delivery_pref
        )
    
    def _extract_quantity(self, query: str, product: str) -> int:
        """Extract quantity for a product from query"""
        import re
        
        # Look for patterns like "2 kg rice", "3 milk", "5 bread"
        patterns = [
            rf"(\d+)\s*kg\s*{product}",
            rf"(\d+)\s*{product}",
            rf"{product}\s*(\d+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                return int(match.group(1))
        
        return 1
    
    def _extract_budget(self, query: str) -> Optional[float]:
        """Extract budget constraint from query"""
        import re
        
        # Look for patterns like "under 1000", "less than 5000", "budget 2000", "50k", "under 50k"
        patterns = [
            r"under\s*(\d+)k",  # under 50k
            r"less\s*than\s*(\d+)k",  # less than 50k
            r"(\d+)k",  # 50k
            r"under\s*(\d+)",  # under 1000
            r"less\s*than\s*(\d+)",  # less than 5000
            r"budget\s*(\d+)",  # budget 2000
            r"(\d+)\s*rupees?",  # 1000 rupees
            r"₹\s*(\d+)"  # ₹1000
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                value = float(match.group(1))
                # If the pattern contains 'k', multiply by 1000
                if 'k' in pattern:
                    value *= 1000
                return value
        
        return None
    
    def extract_keywords(self, query: str) -> List[str]:
        """Extract search keywords from query"""
        # Remove common words and extract meaningful keywords
        stop_words = {
            "i", "need", "want", "buy", "get", "find", "search", "for", "and", "or", "the", "a", "an",
            "with", "under", "over", "less", "than", "more", "than", "rupees", "rs", "₹", "can", "could",
            "please", "to", "in", "cart", "add", "looking"
        }
        
        words = query.lower().split()
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords


# Global instance
query_parser = QueryParser()