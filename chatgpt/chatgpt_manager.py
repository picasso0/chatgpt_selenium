from chatgpt.chatgpt_automatic import ChatGPTAutomator
from shutil import rmtree
from time import strptime
from fastapi import HTTPException
from datetime import datetime, timedelta
from asyncio import create_task
from global_vars import WINDOW_EXP_HOUR
from db import DatabaseClass

class UserChatGPTSessionManager:
    def __init__(self):
        self.chatgpt_sessions = {}
    
    async def set_db(self, db:DatabaseClass):
        self.db=db

    async def get_session(self, window_id: int):
        if window_id in self.chatgpt_sessions:
            return self.chatgpt_sessions[window_id]
        else:
            return None
         
    async def create_session(self, gpt_type: int ):
        try:
            window =  await self.db.insert_window(gpt_type)
            window_id = str(window.get("_id"))
            bot_id = str(window.get("bot_id"))
            session = ChatGPTAutomator()
            await session.initialize(db=self.db, window_id=window_id, bot_id=bot_id)
            self.chatgpt_sessions[window_id] = {'session':session , "window_id": window_id}
            return self.chatgpt_sessions[window_id]
        except HTTPException as e:
            raise e

    async def delete_session(self, window_ids):  
        if type(window_ids) != list:
            window_ids = [window_ids]
        for window_id in window_ids:
            print(f"deleting {window_id}")
            window_id = str(window_id)
            try:
                window_status =  await self.db.delete_user_window(window_id)
                self.chatgpt_sessions[window_id]['session'].quit()
                del self.chatgpt_sessions[window_id]
            except:
                pass
            try:
                rmtree(window_id)
            except:
                pass

chatgpt_session_manager = UserChatGPTSessionManager()