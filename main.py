import sys
if sys.platform.startswith('win'):
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.api.v1.api import api_router
from app.database.mongodb import connect_to_mongo, close_mongo_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - only connect if MongoDB URL is provided
    if settings.MONGODB_URL:
        await connect_to_mongo()
    yield
    # Shutdown
    if settings.MONGODB_URL:
        await close_mongo_connection()


app = FastAPI(
    title="SmartShop API",
    description="A unified shopping assistant that compares prices across e-commerce and instant delivery platforms",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Custom CORS middleware for Vercel deployment
class CustomCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Handle preflight OPTIONS requests
        if request.method == "OPTIONS":
            from fastapi.responses import Response
            response = Response(content="OK")
            response.headers["Access-Control-Allow-Origin"] = "https://smart-shop-frontend-git-master-anushka-pimpales-projects.vercel.app"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
            response.headers["Access-Control-Allow-Headers"] = "Origin, X-Requested-With, Content-Type, Accept, Authorization"
            response.headers["Access-Control-Max-Age"] = "86400"
            return response
        
        response = await call_next(request)
        
        # Add CORS headers to all responses
        response.headers["Access-Control-Allow-Origin"] = "https://smart-shop-frontend-git-master-anushka-pimpales-projects.vercel.app"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "Origin, X-Requested-With, Content-Type, Accept, Authorization"
        
        return response

# Add custom CORS middleware
app.add_middleware(CustomCORSMiddleware)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "message": "Welcome to SmartShop API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }




@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "smartshop-backend"}


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code}
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False,  # Disable reload in production
        log_level="info"
    ) 