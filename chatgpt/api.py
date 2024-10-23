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
    await chatgpt_session_manager.check_bots_time_limitation()
    user_id = str(current_user)
    gpt_type = input.type
    incognito = None
    breakpoint()
    try:
        incognito = input.incognito
    except:
        incognito = None
    window_id = None
    try:
        session = await chatgpt_session_manager.create_session(gpt_type=gpt_type, incognito=incognito)
        if not session:
            print("در ساخت نشست چت جی پی تی مشکلی رخ داده است مجددا تلاش نمایید")
            return JSONResponse(content={"answer":"در ساخت نشست چت جی پی تی مشکلی رخ داده است مجددا تلاش نمایید"}, status_code=400)
        
        bot_id = session.get("bot_id")

        try:
            chatgpt = session.get("session")
        except:
            await chatgpt_session_manager.delete_session(window_id)
            await chatgpt_session_manager.handle_bot_error(bot_id, "get session fault")
            
            print("سشن با مشکل مواجه شده است مجددا تلاش کنید .",window_id)
            
            return JSONResponse(content={"answer":"سشن با مشکل مواجه شده است مجددا تلاش کنید ."}, status_code=400)
        if chatgpt:
            try:
                if not incognito:
                    if not chatgpt.create_new_chat():
                        await chatgpt_session_manager.handle_bot_error(bot_id, "bot loged out", 0)
                        return JSONResponse(content={"answer":f"plese try again selected bot was loged out  ."}, status_code=400)
                    
                window_id = session.get("window_id")
                now_datetime=datetime.now()
                if not chatgpt.send_prompt_to_chatgpt(input.promt):
                    await chatgpt_session_manager.handle_bot_error(bot_id, "1 hour limitation", 2)
                    return JSONResponse(content={"answer":"1 hour limitation ."}, status_code=400)
                    
                if chatgpt.show_check_verify():
                    await chatgpt_session_manager.delete_session(window_id)
                    await chatgpt_session_manager.handle_bot_error(bot_id, "captcha error")
                    return JSONResponse(content={"answer":"لطفا مجددا تلاش فرمایید خطای کپچا ."}, status_code=400)
            
                answer = chatgpt.return_last_response()
                await db.insert_userchat(window_id=window_id, user_id=user_id, now_datetime=now_datetime, promt=input.promt, answer=answer)
                await chatgpt_session_manager.delete_session(window_id)
                return JSONResponse(content={"window_id":window_id, "answer":answer}, status_code=200)
            except: 
                pass
        
        await chatgpt_session_manager.delete_session(window_id)
        await chatgpt_session_manager.handle_bot_error(bot_id, "use chatgpt session faild")
        
        print("error in create chatgpt session",window_id)
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
