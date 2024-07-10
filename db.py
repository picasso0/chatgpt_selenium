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
        self.db = self.client.chatgpt

    async def check_connection(self):
        try:
            await self.db.command("serverStatus")
            return self.db
        except Exception as e:
            return False
        
    async def insert_window(self, gpt_type: str, public: int = 0):
        now_datetime = datetime.now()
        bot = await self.db.bots.find_one(sort=[("windows_number", 1)])
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
            await self.db.bots.update_one({"_id":ObjectId(bot_id)},{'$inc': {'window_counts': -1}})
            await self.db.windows.update_one({"_id":ObjectId(window_id)},{"$set":{"status":0}})

    async def update_window(self, window_id: str, data: dict):
        window = await self.db.windows.update_one({"_id":ObjectId(window_id)},data)
        return window

    async def select_enable_window(self, gpt_type):
        # Get all bots with status 1
        bots = await self.db.bots.find({"type": gpt_type}).to_list(length=None)
        expired_windows = []
        for bot in bots:
            windows = await self.db.windows.find({"bot_id" : bot['_id'], "status": 1},sort=[("_id", 1)]).to_list(length=None)
            for window in windows:
                if window.get("last_used"):
                    window_last_used_datetime = window.get("last_used")
                    now_datetime = datetime.now()
                    if now_datetime > window_last_used_datetime + timedelta(hours=int(WINDOW_EXP_HOUR)):
                        expired_windows.append(window.get("_id"))
                    else:
                        return window,expired_windows
        return None, expired_windows
    
    async def select_enable_public_window(self, gpt_type):
        bots = await self.db.bots.find({"type": gpt_type}).to_list(length=None)
        expired_windows = []
        for bot in bots:
            window = await self.db.windows.find_one({"bot_id" : bot['_id'], "status": 1, "public_window": 1})
            if window:
                if window.get("last_used"):
                    window_last_used_datetime = window.get("last_used")
                    now_datetime = datetime.now()
                    if now_datetime > window_last_used_datetime + timedelta(hours=int(PUBLIC_WINDOW_EXP_HOUR)):
                        expired_windows.append(window.get("_id"))
                    else:
                        return window,expired_windows
        return None, expired_windows
        
    async def check_public_windows(self, gpt_type):
        bot_counts = await self.db.bots.count_documents({"type": gpt_type})
        window_counts = await self.db.windows.count_documents({"status": 2, "public_window": 1})
        if bot_counts == window_counts:
            return 0
        return 1
       
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
        check_userchats_existence = await self.db.userchats.find_one({"user_id": user_id, "window_id": window_id})
        if check_userchats_existence:
            userchat = await self.db.userchats.update_one({"_id":check_userchats_existence['_id']}, {"$push":{"chats": chat_data}})
        else:
            userchat = await self.db.userchats.insert_one({"window_id": window_id, "user_id": user_id, "chats": [chat_data]})