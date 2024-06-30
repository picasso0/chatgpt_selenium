from chatgpt.chatgpt_automatic import ChatGPTAutomator
from time import strptime
from datetime import datetime, timedelta
from db import insert_window, delete_user_window, select_enable_window, get_window, update_window
class UserChatGPTSessionManager:
    def __init__(self):
        self.chatgpt_sessions = {}

    async def get_session(self, window_id: int):
        if window_id in self.chatgpt_sessions:
            return self.chatgpt_sessions[window_id]
        else:
            return None

    async def create_session(self, bot_id: str, user_id: str, gpt_type: int ):
        try:
            window = await select_enable_window(bot_id=bot_id)
            if not window:
                window = await insert_window(bot_id)
                window_id = str(window.get("_id"))
                session = ChatGPTAutomator()
                await session.initialize(window_id=window_id, gpt_type=gpt_type)
                self.chatgpt_sessions[window_id] = {'session':session, 'user_id':user_id , "window_id": window_id}
            else:
                window_id = str(window.get("_id"))
                self.chatgpt_sessions[window_id]['user_id'] = user_id
            return self.chatgpt_sessions[window_id]
        except:
            await update_window(window_id=window_id,data={"$set":{"status":0}})
            return None

    async def delete_session(self, window_id: int):
        if window_id in self.chatgpt_sessions:
            self.chatgpt_sessions[window_id]['user_id'] = None
            window_status = await delete_user_window(window_id)
            if window_status == 1:
                self.chatgpt_sessions[window_id].quit()
                del self.chatgpt_sessions[window_id]
    
    async def check_window_status(self, window_id):
        window = await get_window(window_id=window_id)
        if not window:
            await self.delete_session(window_id=window_id)
            return 0
        window_status = window.get("status")
        if window_status == 1 :
            if window.get("last_used"):
                window_last_used_datetime = window.get("last_used")
                now_datetime = datetime.now()
                if now_datetime > window_last_used_datetime + timedelta(minutes=20):
                    await self.delete_session(window_id=window_id)
                    return 0
        return window_status
            
        

chatgpt_session_manager = UserChatGPTSessionManager()