from chatgpt_automatic import ChatGPTAutomator

class UserChatGPTSessionManager:
    def __init__(self):
        self.chatgpt_sessions = {}

    def get_session(self, user_id: int):
        if user_id in self.chatgpt_sessions:
            return self.chatgpt_sessions[user_id]
        else:
            return None

    def create_session(self, user_id: int):
        try:
            session = ChatGPTAutomator(user_id)
            self.chatgpt_sessions[user_id] = session
            return session
        except:
            return None

    def delete_session(self, user_id: int):
        if user_id in self.chatgpt_sessions:
            self.chatgpt_sessions[user_id].quit()
            del self.chatgpt_sessions[user_id]

user_chatgpt_session_manager = UserChatGPTSessionManager()