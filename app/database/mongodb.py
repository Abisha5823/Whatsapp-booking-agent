from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

mongodb = MongoDB()

async def connect_to_mongo():
    """Establish connection to MongoDB Atlas"""
    try:
        mongodb.client = AsyncIOMotorClient(settings.MONGODB_URL)
        mongodb.db = mongodb.client[settings.MONGODB_DB_NAME]
        
        # Test connection
        await mongodb.client.admin.command('ping')
        
        # Create indexes for better performance
        await mongodb.db.bookings.create_index("booking_id", unique=True)
        await mongodb.db.bookings.create_index("whatsapp_number")
        await mongodb.db.bookings.create_index([("preferred_date", 1), ("booking_status", 1)])
        await mongodb.db.sessions.create_index("whatsapp_number", unique=True)
        await mongodb.db.sessions.create_index("updated_at", expireAfterSeconds=604800)  # Auto-delete after 7 days
        
        logger.info("✅ Connected to MongoDB Atlas")
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        raise

async def close_mongo_connection():
    """Close MongoDB connection"""
    if mongodb.client:
        mongodb.client.close()
        logger.info("MongoDB connection closed")

def get_db():
    """Get database instance"""
    if mongodb.db is None:
        raise Exception("Database not connected. Call connect_to_mongo() first")
    return mongodb.db