from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Global database client
client: AsyncIOMotorClient = None
database = None


async def connect_to_mongo():
    """Create database connection."""
    global client, database
    try:
        # Check if MongoDB is configured
        if not settings.MONGODB_URL:
            logger.info("MongoDB not configured - running in memory-only mode")
            return
            
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        database = client[settings.MONGODB_DB_NAME]
        
        # Test the connection
        await client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        logger.info("Running in memory-only mode")
        client = None
        database = None


async def close_mongo_connection():
    """Close database connection."""
    global client
    if client:
        client.close()
        logger.info("MongoDB connection closed")


def get_database():
    """Get database instance."""
    return database


def get_collection(collection_name: str):
    """Get collection instance."""
    if database is None:
        raise RuntimeError("MongoDB not configured - cannot access collections")
    return database[collection_name] 