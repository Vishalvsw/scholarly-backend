from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
import logging
logger = logging.getLogger(__name__)
class MongoDB:
    client: AsyncIOMotorClient = None
    database = None
mongodb = MongoDB()
async def connect_to_mongo():
    try:
        mongodb.client = AsyncIOMotorClient(settings.MONGODB_URL)
        mongodb.database = mongodb.client[settings.DATABASE_NAME]
        await create_indexes()
        logger.info("Connected to MongoDB")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise
async def close_mongo_connection():
    if mongodb.client:
        mongodb.client.close()
        logger.info("Closed MongoDB connection")
async def create_indexes():
    db = mongodb.database
    await db.users.create_index("email", unique=True)
    await db.users.create_index("username", unique=True)
    await db.papers.create_index("title")
    await db.papers.create_index("status")
    await db.papers.create_index("author_id")
    await db.papers.create_index([("submitted_at", -1)])
    await db.subscriptions.create_index("email", unique=True)
def get_database():
    return mongodb.database
