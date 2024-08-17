import motor.motor_asyncio
from bson import ObjectId
from fastapi import HTTPException
from global_vars import MONGODB_URL
from datetime import datetime, timedelta
from shutil import rmtree
from global_vars import WINDOW_EXP_HOUR, PUBLIC_WINDOW_EXP_HOUR

async def get_db():
    db = DatabaseClass()
    db_connection = await db.check_connection()
    if db_connection==0:
        return 0
    return db
        
class DatabaseClass:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
        self.db = self.client.chatgpt_new

    async def check_connection(self):
        try:
            await self.db.command("serverStatus")
            return self.db
        except Exception as e:
            return False
        
    async def insert_window(self, gpt_type: str, public: int = 0):
        now_datetime = datetime.now()
        bot = await self.db.bots.find_one(sort=[("window_counts", 1)])
        window_data = {'bot_id':ObjectId(bot['_id']), 'create_at':now_datetime, 'status':2, "public_window": public}
        window = await self.db.windows.insert_one(window_data)
        await self.db.bots.update_one({"_id":ObjectId(bot['_id'])},{'$inc': {'window_counts': 1}})
        window = await self.db.windows.find_one({"_id":window.inserted_id})
        return window

    async def delete_user_window(self, window_id: str):
        now_datetime = datetime.now()
        window = await self.db.windows.find_one({"_id":ObjectId(window_id)})
        if window.get("status") == 1:
            bot_id = window.get("bot_id")
            await self.db.windows.update_one({"_id":ObjectId(window_id)},{"$set":{"status":0}})

    async def get_window(self, window_id):
        window = await self.db.windows.find_one({"_id":ObjectId(window_id)})
        return window

    # BOTS
    async def get_user_data_url(self, bot_id):
        bot = await self.db.bots.find_one({"_id":ObjectId(bot_id)})
        return bot.get("userdata")

    # USER CHAT
    async def insert_userchat(self, window_id: ObjectId, user_id: ObjectId ,now_datetime: datetime, promt: str, answer:str ):
        chat_data = {"created_at": now_datetime, "promt": promt, "answer": answer}
        userchat = await self.db.userchats.insert_one({"window_id": window_id, "user_id": user_id, "chats": [chat_data]})