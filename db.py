from time import strptime
from os import remove
import motor.motor_asyncio
from bson import ObjectId
from datetime import datetime, timedelta
from global_vars import MONGODB_URL, WINDOW_EXP_MIN

async def get_database():
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
    db = client.chatgpt
    return db

# WINDOWS
async def insert_window(gpt_type: str):
    db = await get_database()
    now_datetime = datetime.now()
    bot = await db.bots.find_one(sort=[("windows_number", 1)])
    window_data = {'bot_id':ObjectId(bot['_id']), 'create_at':now_datetime, 'status':1}
    window = await db.windows.insert_one(window_data)
    await db.bots.update_one({"_id":ObjectId(bot['_id'])},{'$inc': {'window_counts': 1}})
    window = await db.windows.find_one({"_id":window.inserted_id})
    return window

async def delete_user_window(window_id: str):
    db = await get_database()
    now_datetime = datetime.now()
    window = await db.wondows.find_one({"_id":ObjectId(window_id)})
    bot_id = window.get("bot_id")
    await db.bots.update_one({"_id":ObjectId(bot_id)},{'$inc': {'window_counts': -1}})
    window_last_used_datetime = strptime(window.get("last_used"), "%Y-%m-%d %H:%M:%S")
    if now_datetime > window_last_used_datetime + timedelta(minutes=int(WINDOW_EXP_MIN)):
        await db.wondows.update_one({"_id":ObjectId(window_id)},{"$set":{"status":0}})
        return 1
    await db.wondows.update_one({"_id":ObjectId(window_id)},{"$set":{"status":1}})
    return 0


async def update_window(window_id: str, data: dict):
    db = await get_database()
    window = await db.windows.update_one({"_id":ObjectId(window_id)},data)
    return window

async def select_enable_window(gpt_type):
    db = await get_database()

    # Get all bots with status 1
    bots = await db.bots.find({"type": 1}).to_list(length=None)
    
    for bot in bots:
        windows = await db.windows.find({"bot_id" : bot['_id'], "status": 1}).to_list(length=None)
        for window in windows:
            if window.get("last_used"):
                window_last_used_datetime = window.get("last_used")
                now_datetime = datetime.now()
                if now_datetime > window_last_used_datetime + timedelta(minutes=int(WINDOW_EXP_MIN)):
                    await db.windows.update_one({"_id":ObjectId(window['_id'])},{"$set":{"status":0}})
                    await db.bots.update_one({"_id":ObjectId(window['bot_id'])},{'$inc': {'window_counts': -1}})
                    try:
                        remove(str(window['_id']))
                    except:
                        pass
                else:
                    return window
    return None
    
    
    
    
    window = await db.windows.find_one({"bot_id":ObjectId(bot_id),"status":1})
    if not window:
        return None
    if window.get("last_used"):
        window_last_used_datetime = window.get("last_used")
        now_datetime = datetime.now()
        if now_datetime > window_last_used_datetime + timedelta(minutes=int(WINDOW_EXP_MIN)):
            return None
    return window

async def get_window(window_id):
    db = await get_database()
    window = await db.windows.find_one({"_id":ObjectId(window_id)})
    return window



# BOTS
async def get_user_data_url(bot_id):
    db = await get_database()
    bot = await db.bots.find_one({"_id":ObjectId(bot_id)})
    return bot.get("userdata")



#USER CHAT
async def insert_userchat(window_id: ObjectId, user_id: ObjectId ,now_datetime: datetime, promt: str, answer:str ):
    db = await get_database()
    chat_data = {"created_at": now_datetime, "promt": promt, "answer": answer}
    check_userchats_existence = await db.userchats.find_one({"user_id": user_id, "window_id": window_id})
    if check_userchats_existence:
        userchat = await db.userchats.update_one({"_id":check_userchats_existence['_id']}, {"$push":{"chats": chat_data}})
    else:
        userchat = await db.userchats.insert_one({"window_id": window_id, "user_id": user_id, "chats": [chat_data]})
