from chatgpt.chatgpt_automatic import ChatGPTAutomator
from shutil import rmtree
from time import strptime
from fastapi import HTTPException
from datetime import datetime, timedelta
from asyncio import create_task
from global_vars import WINDOW_EXP_MIN

class UserChatGPTSessionManager:
    def __init__(self):
        self.chatgpt_sessions = {}
    
    async def set_db(self, db):
        self.db=db

    async def get_session(self, window_id: int):
        if window_id in self.chatgpt_sessions:
            return self.chatgpt_sessions[window_id]
        else:
            return None

    async def create_session(self, gpt_type: int ):
        try:
            window, expired_windows =  await self.db.select_enable_window(gpt_type)
            task = None
            for expire_window in expired_windows:
                task = create_task(self.delete_session(expire_window))
            if not window:
                window =  await self.db.insert_window(gpt_type)
                window_id = str(window.get("_id"))
                bot_id = str(window.get("bot_id"))
                session = ChatGPTAutomator()
                await session.initialize(db=self.db, window_id=window_id, bot_id=bot_id)
                self.chatgpt_sessions[window_id] = {'session':session , "window_id": window_id}
                if task:
                    await task
            else:
                window_id = str(window.get("_id"))
            return self.chatgpt_sessions[window_id]
        except HTTPException as e:
            raise e
        except:
            try:
                 await self.db.update_window(window_id=window_id,data={"$set":{"status":0}})
            except:
                pass
            return None

    async def delete_session(self, window_ids):  
        if type(window_ids) != list:
            window_ids = [window_ids]
        for window_id in window_ids:
            print(f"deleting {window_id}")
            window_id = str(window_id)
            try:
                window_status =  await self.db.delete_user_window(window_id)
                self.chatgpt_sessions[window_id].quit()
                del self.chatgpt_sessions[window_id]
            except:
                pass
            try:
                rmtree(window_id)
            except:
                pass
        
    async def check_window_status(self, window_id):
        window =  await self.db.get_window(window_id=window_id)
        if window != 1:
            create_task(self.delete_session(window_id) )
            return 0
        window_status = window.get("status")
        if window.get("last_used"):
            window_last_used_datetime = window.get("last_used")
            now_datetime = datetime.now()
            if now_datetime > window_last_used_datetime + timedelta(int(WINDOW_EXP_MIN)):
                create_task(self.delete_session(window_id) )
                return 0
        return window_status
            
        

chatgpt_session_manager = UserChatGPTSessionManager()