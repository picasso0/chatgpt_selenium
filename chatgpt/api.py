from fastapi.responses import JSONResponse
from fastapi import APIRouter ,Depends, Body
from auth.auth import get_current_bot
from chatgpt.schema import Question, Promt
from datetime import datetime
from chatgpt.chatgpt_manager import chatgpt_session_manager
from db import update_window

app = APIRouter()

@app.get("/create_chatgpt_session")
async def create_chatgpt_session(current_bot: dict = Depends(get_current_bot)):
    existed_session=chatgpt_session_manager.get_session(str(current_bot.get('_id')))
    if existed_session:
        return {"msg":"chatgpt session created before"}
    user_id = str(current_bot.get('_id'))
    chatgpt_session_manager.create_session(user_id)
    return JSONResponse(content={"msg":"chatgpt session created"}, status_code=200)
    

@app.post("/quit/")
async def quit(current_bot: dict = Depends(get_current_bot)):
    user_id = str(current_bot.get('_id'))
    try:
        chatgpt = chatgpt_session_manager.get_session(user_id)
        chatgpt.quit()
        return JSONResponse(content={"msg":"chatgpt session quited"}, status_code=200)
    except:
        return JSONResponse(content={"msg":"you dont have any chatgpt session ."}, status_code=400)




@app.post("/sendPromt/")
async def send_prompt(current_bot: dict = Depends(get_current_bot), input: Promt=Body()):
    user_id = str(current_bot.get('_id'))
    gpt_type = input.type
    if input.window_id:
        window_id = input.window_id
        window_status = await chatgpt_session_manager.check_window_status(window_id)
        if window_status != 1:
            return JSONResponse(content={"answer":"این صفحه منقضی شده است"}, status_code=400)
        session = await chatgpt_session_manager.get_session(window_id=window_id)
    else: 
        session = await chatgpt_session_manager.create_session(user_id=user_id, bot_id=user_id, gpt_type=gpt_type)
        if not session:
            return JSONResponse(content={"answer":"این صفحه منقضی شده است"}, status_code=400)
        window_id = session.get("window_id")
    try:
        chatgpt = session.get("session")
    except:
        await chatgpt_session_manager.delete_session(window_id=window_id)   
        return JSONResponse(content={"answer":"سشن با مشکل مواجه شده است مجددا تلاش کنید ."}, status_code=400)
    
    if chatgpt:
        now_datetime=datetime.now()
        await update_window(window_id=window_id,data={"$set":{"last_used":now_datetime}})
        chatgpt.send_prompt_to_chatgpt(input.promt)
        answer = chatgpt.return_last_response()
        return JSONResponse(content={"window_id":window_id, "answer":answer}, status_code=200)
    else:
        await chatgpt_session_manager.delete_session(window_id=window_id)   
        return JSONResponse(content={"answer":"error in create chatgpt session"}, status_code=400)
