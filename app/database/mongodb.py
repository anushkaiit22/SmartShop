from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Try to import motor, but make it optional for Vercel deployment
try:
    from motor.motor_asyncio import AsyncIOMotorClient
    MOTOR_AVAILABLE = True
except ImportError:
    AsyncIOMotorClient = None
    MOTOR_AVAILABLE = False
    logger.info("Motor (MongoDB driver) not available - running in memory-only mode")

# Global database client
client = None
database = None


async def connect_to_mongo():
    """Create database connection."""
    global client, database
    try:
        # Check if MongoDB is configured and motor is available
        if not settings.MONGODB_URL or not MOTOR_AVAILABLE:
            logger.info("MongoDB not configured or motor not available - running in memory-only mode")
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
    if client and MOTOR_AVAILABLE:
        client.close()
        logger.info("MongoDB connection closed")


def get_database():
    """Get database instance."""
    return database


def get_collection(collection_name: str):
    """Get collection instance."""
    if database is None or not MOTOR_AVAILABLE:
        raise RuntimeError("MongoDB not configured or motor not available - cannot access collections")
    return database[collection_name] 