from fastapi.responses import JSONResponse
from fastapi import APIRouter ,Depends, Body, HTTPException
from auth.auth import get_current_user
from chatgpt.schema import Question, Promt
from datetime import datetime
from chatgpt.chatgpt_manager import chatgpt_session_manager
from db import get_db
from asyncio import create_task
from time import sleep
app = APIRouter()


@app.post("/sendPromt/")
async def send_prompt(current_user: dict = Depends(get_current_user), input: Promt=Body()):
    db = await get_db()
    if db==0:
        return JSONResponse(content={"answer":"اتصال به دیتابیس با مشکل مواجه شده است"}, status_code=400)
    await chatgpt_session_manager.set_db(db)
    user_id = str(current_user)
    gpt_type = input.type
    window_id = None
    try:
        if input.single_promt==1:
            session = await chatgpt_session_manager.create_public_session(gpt_type=gpt_type)
            if session==0:
                return JSONResponse(content={"answer":"صفحات درحال استفاده هستند لطفا مجددا تلاش نمایید ."}, status_code=400)
            session.get("session").create_new_chat()
            sleep(0.5)
        elif input.window_id:
            window_id = input.window_id
            window_status = await chatgpt_session_manager.check_window_status(window_id)
            if window_status == 2:
                return JSONResponse(content={"answer":"این صفحه درحال استفاده است لطفا مجددا تلاش نمایید ."}, status_code=400)
            elif window_status == 0:
                return JSONResponse(content={"answer":"این صفحه منقضی شده است"}, status_code=400)
            session = await chatgpt_session_manager.get_session(window_id=window_id)
        else: 
            session = await chatgpt_session_manager.create_session(gpt_type=gpt_type)
            if not session:
                return JSONResponse(content={"answer":"در ساخت نشست چت جی پی تی مشکلی رخ داده است مجددا تلاش نمایید"}, status_code=400)
        try:
            chatgpt = session.get("session")
            await db.update_window(window_id=window_id,data={"$set":{"status":2}})
        except:
            # create_task(chatgpt_session_manager.delete_session(window_id) )
            await chatgpt_session_manager.delete_session(window_id)
            return JSONResponse(content={"answer":"سشن با مشکل مواجه شده است مجددا تلاش کنید ."}, status_code=400)
        
        if chatgpt:
            window_id = session.get("window_id")
            now_datetime=datetime.now()
            await db.update_window(window_id=window_id,data={"$set":{"last_used":now_datetime, "status":2}})
            chatgpt.send_prompt_to_chatgpt(input.promt)
            answer = chatgpt.return_last_response()
            await db.update_window(window_id=window_id,data={"$set":{"status":1}})
            await db.insert_userchat(window_id=window_id, user_id=user_id, now_datetime=now_datetime, promt=input.promt, answer=answer)
            return JSONResponse(content={"window_id":window_id, "answer":answer}, status_code=200)
        else:
            # create_task(chatgpt_session_manager.delete_session(window_id) )   
            await chatgpt_session_manager.delete_session(window_id)
            return JSONResponse(content={"answer":"error in create chatgpt session"}, status_code=400)
    except HTTPException as e:
        raise e



# @app.post("/quit/")
# async def quit(current_user: dict = Depends(get_current_user)):
#     user_id = str(current_user.get('_id'))
#     try:
#         chatgpt = chatgpt_session_manager.get_session(user_id)
#         chatgpt.quit()
#         return JSONResponse(content={"msg":"chatgpt session quited"}, status_code=200)
#     except:
#         return JSONResponse(content={"msg":"you dont have any chatgpt session ."}, status_code=400)
