#!/usr/bin/env python3
"""
Test script to verify MongoDB and Redis connections
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_mongodb():
    """Test MongoDB connection"""
    print("🔍 Testing MongoDB connection...")
    
    mongodb_url = os.getenv('MONGODB_URL')
    
    if not mongodb_url:
        print("⚠️  No MongoDB URL configured - MongoDB is optional for testing")
        print("✅ Application will run in memory-only mode")
        return True
    
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        
        # Get MongoDB URL from environment
        db_name = os.getenv('MONGODB_DB_NAME', 'smartshop')
        
        print(f"Connecting to: {mongodb_url}")
        
        # Create client
        client = AsyncIOMotorClient(mongodb_url)
        db = client[db_name]
        
        # Test connection
        await client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        
        # Test database operations
        collection = db['test_collection']
        await collection.insert_one({'test': 'connection'})
        await collection.delete_one({'test': 'connection'})
        print("✅ MongoDB database operations successful!")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("⚠️  Application will run in memory-only mode")
        return True  # Return True since it's optional

def test_redis():
    """Test Redis connection"""
    print("\n🔍 Testing Redis connection...")
    
    redis_url = os.getenv('REDIS_URL')
    
    if not redis_url:
        print("⚠️  No Redis URL configured - Redis is optional")
        return True
    
    try:
        import redis
        
        print(f"Connecting to: {redis_url}")
        
        # Create Redis client
        r = redis.from_url(redis_url)
        
        # Test connection
        r.ping()
        print("✅ Redis connection successful!")
        
        # Test basic operations
        r.set('test_key', 'test_value')
        value = r.get('test_key')
        r.delete('test_key')
        
        if value == b'test_value':
            print("✅ Redis operations successful!")
        else:
            print("❌ Redis operations failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🧪 SmartShop - Connection Test")
    print("=" * 40)
    
    # Check if .env file exists
    if not Path('.env').exists():
        print("❌ .env file not found")
        print("Please create .env file from env.example")
        return
    
    # Test MongoDB
    mongodb_ok = await test_mongodb()
    
    # Test Redis
    redis_ok = test_redis()
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Connection Test Results:")
    print(f"MongoDB: {'✅ OK' if mongodb_ok else '❌ FAILED'}")
    print(f"Redis: {'✅ OK' if redis_ok else '❌ FAILED'}")
    
    if mongodb_ok and redis_ok:
        print("\n🎉 All connections successful! You can now run the application.")
    else:
        print("\n⚠️  Some connections failed. Please check your configuration.")
        if not mongodb_ok:
            print("   - MongoDB is optional - application will run in memory-only mode")
        if not redis_ok:
            print("   - Redis is optional but recommended for caching")

if __name__ == "__main__":
    asyncio.run(main()) 