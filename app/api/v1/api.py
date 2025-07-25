from fastapi import APIRouter
from .endpoints import search, cart, query, robot

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(cart.router, prefix="/cart", tags=["cart"])
api_router.include_router(query.router, prefix="/query", tags=["query"])
api_router.include_router(robot.router, prefix="/robot", tags=["robot"]) 