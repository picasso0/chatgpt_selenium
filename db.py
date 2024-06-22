import motor.motor_asyncio
from global_vars import MONGODB_URL

async def get_database():
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
    db = client.chatgpt
    return db
