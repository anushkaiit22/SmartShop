#!/usr/bin/env python3
"""
Test script to verify OpenAI API fix
"""
import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.nlp.query_parser import query_parser

async def test_openai_parsing():
    """Test the OpenAI query parsing"""
    print("Testing OpenAI query parsing...")
    
    # Test queries
    test_queries = [
        "I need milk",
        "buy a laptop under 50000",
        "red t-shirt size L",
        "gaming mouse with good rating"
    ]
    
    for query in test_queries:
        try:
            print(f"\nTesting query: '{query}'")
            result = await query_parser.parse_query(query)
            print(f"Success! Found {len(result.products)} products:")
            for product in result.products:
                print(f"  - {product.product_name} (qty: {product.quantity})")
        except Exception as e:
            print(f"Error parsing '{query}': {e}")

if __name__ == "__main__":
    asyncio.run(test_openai_parsing()) 