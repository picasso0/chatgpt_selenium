from fastapi import FastAPI, HTTPException, Header,Query, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
from schemas import UserInRequest, Token, Question
from chatgpt_manager import user_chatgpt_session_manager
from auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    HTTPException,
)

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

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
async def chat(current_user: dict = Depends(get_current_user), input: Question=Body()):
    if input.question==None or input.question=="":
        return "enter a message"
    user_id = str(current_user.get('_id'))
    chatgpt = user_chatgpt_session_manager.get_session(user_id)
    if chatgpt:
        try:
            chatgpt.send_prompt_to_chatgpt(input.question)
            answer = chatgpt.return_last_response()

            return {"answer":answer}
        except:
            chatgpt = user_chatgpt_session_manager.get_session(user_id)
            chatgpt.quit()
            user_chatgpt_session_manager.delete_session(user_id)
            return {"msg":"create another gpt session"} 
    else:
        return {"answer":"you dont have any chatgpt session ."}


@app.post("/quit/")
async def quit(current_user: dict = Depends(get_current_user)):
    user_id = str(current_user.get('_id'))
    try:
        chatgpt = user_chatgpt_session_manager.get_session(user_id)
        chatgpt.quit()
        return {"msg":"chatgpt session quited"}
    except:
        return {"msg":"you dont have any chatgpt session ."}

