import openai
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import json
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

# Configure OpenAI
if settings.OPENAI_API_KEY:
    openai.api_key = settings.OPENAI_API_KEY


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
        You are a shopping assistant that parses natural language queries into structured product intents.
        
        Your task is to extract:
        1. Product names and quantities
        2. Categories and brands
        3. Price constraints
        4. Rating preferences
        5. Overall budget and delivery preferences
        
        Return a JSON object with the following structure:
        {
            "products": [
                {
                    "product_name": "string",
                    "quantity": number,
                    "category": "string (optional)",
                    "brand": "string (optional)",
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
        - "I need 2 kg rice and a laptop under 50000" → Extract rice (2kg) and laptop (max 50000)
        - "Buy milk, bread, and a smartphone with 4+ rating" → Extract items with rating constraint
        - "Get groceries for under 1000 rupees with fast delivery" → Extract budget and delivery preference
        """
    
    async def parse_query(self, query: str) -> ParsedQuery:
        """Parse natural language shopping query"""
        try:
            if not settings.OPENAI_API_KEY:
                # Fallback to simple parsing if OpenAI is not configured
                return self._simple_parse(query)
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Parse this shopping query: {query}"}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            parsed_data = json.loads(content)
            
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
        """Simple fallback parser using keyword matching"""
        query_lower = query.lower()
        
        # Extract common product keywords
        products = []
        
        # Common grocery items
        grocery_items = ["milk", "bread", "rice", "sugar", "salt", "oil", "flour", "eggs", "butter"]
        for item in grocery_items:
            if item in query_lower:
                quantity = self._extract_quantity(query_lower, item)
                products.append(ProductIntent(
                    product_name=item,
                    quantity=quantity,
                    category="grocery"
                ))
        
        # Electronics
        electronics = ["laptop", "phone", "smartphone", "headphones", "charger", "cable"]
        for item in electronics:
            if item in query_lower:
                products.append(ProductIntent(
                    product_name=item,
                    quantity=1,
                    category="electronics"
                ))
        
        # Extract budget constraints
        budget = self._extract_budget(query_lower)
        
        # Extract delivery preference
        delivery_pref = None
        if any(word in query_lower for word in ["fast", "quick", "urgent", "immediate"]):
            delivery_pref = "fast"
        elif any(word in query_lower for word in ["cheap", "economical", "budget"]):
            delivery_pref = "cheap"
        
        constraints = QueryConstraints(
            total_budget=budget,
            delivery_preference=delivery_pref
        )
        
        return ParsedQuery(
            products=products,
            constraints=constraints,
            original_query=query,
            confidence_score=0.6
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
            "with", "under", "over", "less", "than", "more", "than", "rupees", "rs", "₹"
        }
        
        words = query.lower().split()
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords


# Global instance
query_parser = QueryParser() 