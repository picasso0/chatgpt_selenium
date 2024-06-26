from time import strptime
import motor.motor_asyncio
from bson import ObjectId
from datetime import datetime, timedelta
from global_vars import MONGODB_URL

async def get_database():
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
    db = client.chatgpt
    return db

# WINDOWS
async def insert_window(bot_id: str):
    db = await get_database()
    now_datetime = datetime.now()
    window_data = {'bot_id':ObjectId(bot_id), 'createAt':str(now_datetime), 'status':1}
    window = await db.windows.insert_one(window_data)
    aaa = await db.bots.update_one({"_id":ObjectId(bot_id)},{'$inc': {'window_counts': 1}})
    window = await db.windows.find_one({"_id":window.inserted_id})
    return window

async def delete_user_window(window_id: str):
    db = await get_database()
    now_datetime = datetime.now()
    window = await db.wondows.find_one({"_id":ObjectId(window_id)})
    bot_id = window.get("bot_id")
    await db.bots.update_one({"_id":ObjectId(bot_id)},{'$inc': {'window_counts': -1}})
    window_last_used_datetime = strptime(window.get("last_used"), "%Y-%m-%d %H:%M:%S")
    if now_datetime > window_last_used_datetime + timedelta(minutes=10):
        await db.wondows.update_one({"_id":ObjectId(window_id)},{"$set":{"status":0}})
        return 1
    await db.wondows.update_one({"_id":ObjectId(window_id)},{"$set":{"status":1}})
    return 0


async def update_window(window_id: str, data: dict):
    db = await get_database()
    window = await db.windows.update_one({"_id":ObjectId(window_id)},data)
    return window

async def select_enable_window(bot_id):
    db = await get_database()
    window = await db.windows.find_one({"bot_id":ObjectId(bot_id),"status":1})
    if not window:
        return None
    if window.get("last_used"):
        window_last_used_datetime = strptime(window.get("last_used"), "%Y-%m-%d %H:%M:%S")
        now_datetime = datetime.now()
        if now_datetime > window_last_used_datetime + timedelta(minutes=10):
            return None
    return window

async def get_window(window_id):
    db = await get_database()
    window = await db.windows.find_one({"_id":ObjectId(window_id)})
    return window



# USERDATA
async def get_user_data_url(gpt_type):
    db = await get_database()
    userdata = await db.userdatas.find_one({"type":gpt_type},sort=[("user_counts", 1)])
    user_data_id = str(userdata.get("_id"))
    await db.userdatas.update_one({"_id":ObjectId(user_data_id)},{'$inc': {'user_counts': 1}})
    return userdata.get("download_url")
