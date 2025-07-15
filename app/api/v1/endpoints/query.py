from fastapi import APIRouter, HTTPException, Body
from typing import Optional
import logging

from app.services.nlp.query_parser import query_parser

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/parse")
async def parse_query(query: str = Body(..., description="Natural language shopping query")):
    """
    Parse natural language shopping query into structured format.
    
    This endpoint uses NLP to extract product intents, quantities, constraints,
    and preferences from natural language queries.
    
    Example queries:
    - "I need 2 kg rice and a laptop under 50000"
    - "Buy milk, bread, and a smartphone with 4+ rating"
    - "Get groceries for under 1000 rupees with fast delivery"
    """
    try:
        parsed_query = await query_parser.parse_query(query)
        
        return {
            "success": True,
            "data": parsed_query,
            "message": "Query parsed successfully"
        }
    except Exception as e:
        logger.error(f"Error parsing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/keywords")
async def extract_keywords(query: str = Body(..., description="Query to extract keywords from")):
    """
    Extract search keywords from a query.
    
    This endpoint removes common words and extracts meaningful keywords
    that can be used for product search.
    """
    try:
        keywords = query_parser.extract_keywords(query)
        
        return {
            "success": True,
            "data": {
                "keywords": keywords,
                "count": len(keywords)
            },
            "message": "Keywords extracted successfully"
        }
    except Exception as e:
        logger.error(f"Error extracting keywords: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 