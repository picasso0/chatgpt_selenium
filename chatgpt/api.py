from main import app
from fastapi.responses import JSONResponse
from fastapi import Depends, Body
from auth.auth import get_current_bot
from chatgpt.schema import Question
from chatgpt.chatgpt_manager import chatgpt_session_manager

@app.get("/create_chatgpt_session")
async def create_chatgpt_session(current_bot: dict = Depends(get_current_bot)):
    existed_session=chatgpt_session_manager.get_session(str(current_bot.get('_id')))
    if existed_session:
        return {"msg":"chatgpt session created before"}
    user_id = str(current_bot.get('_id'))
    chatgpt_session_manager.create_session(user_id)
    return JSONResponse(content={"msg":"chatgpt session created"}, status_code=200)
    

@app.post("/chat/")
async def chat(current_bot: dict = Depends(get_current_bot), input: Question=Body()):
    if input.question==None or input.question=="":
        return "enter a message"
    user_id = str(current_bot.get('_id'))
    chatgpt = chatgpt_session_manager.get_session(user_id)
    if chatgpt:
        chatgpt.send_prompt_to_chatgpt(input.question)
        answer = chatgpt.return_last_response()

        return JSONResponse(content={"answer":answer}, status_code=200)
    else:
        return JSONResponse(content={"answer":"you dont have any chatgpt session ."}, status_code=400)


@app.post("/quit/")
async def quit(current_bot: dict = Depends(get_current_bot)):
    user_id = str(current_bot.get('_id'))
    try:
        chatgpt = chatgpt_session_manager.get_session(user_id)
        chatgpt.quit()
        return JSONResponse(content={"msg":"chatgpt session quited"}, status_code=200)
    except:
        return JSONResponse(content={"msg":"you dont have any chatgpt session ."}, status_code=400)
