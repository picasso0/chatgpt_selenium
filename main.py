from chatgpt_automatic import ChatGPTAutomator
from fastapi import FastAPI, HTTPException, Header,Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    Token,
    UserInRequest,
    oauth2_scheme,
    HTTPException
)
from db import get_database


async def get_db_instance():
    database = await get_database()
    return database


app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

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


@app.post("/token", response_model=Token)
async def login_for_access_token(input: UserInRequest):
    user = await authenticate_user(input.username, input.password)
    if not user:
        credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
        raise credentials_exception
        
        
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/create_chatgpt_session")
async def create_chatgpt_session(current_user: dict = Depends(get_current_user)):
    existed_session=user_chatgpt_session_manager.get_session(str(current_user.get('_id')))
    if existed_session:
        return {"msg":"chatgpt session created before"}
    user_id = str(current_user.get('_id'))
    user_chatgpt_session_manager.create_session(user_id)
    return {"msg":"chatgpt session created"}
    

@app.post("/chat/")
async def chat(current_user: dict = Depends(get_current_user), question:str=Query()):
    if question==None or question=="":
        return "enter a message"
    user_id = str(current_user.get('_id'))
    chatgpt = user_chatgpt_session_manager.get_session(user_id)
    chatgpt.send_prompt_to_chatgpt(question)
    answer = chatgpt.return_last_response()

    return {"answer":answer}


@app.post("/quit/")
async def quit(current_user: dict = Depends(get_current_user)):
    user_id = str(current_user.get('_id'))
    chatgpt = user_chatgpt_session_manager.get_session(user_id)
    chatgpt.quit()
    return {"msg":"chatgpt session quited"}

