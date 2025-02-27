from fastapi.responses import JSONResponse
from fastapi import APIRouter ,Depends, Body, HTTPException
from auth.auth import get_current_user
from chatgpt.schema import Question, Promt
from datetime import datetime
# from chatgpt.chatgpt_automatic_proxy import ChatGPTAutomator
from chatgpt.chatgpt_automatic import ChatGPTAutomator
from utils.db import get_db
from asyncio import create_task
from time import sleep
app = APIRouter()


@app.post("/sendPromt/")
async def send_prompt(input: Promt=Body()):
    gpt_type = input.type
    incognito = 1
    chatgpt = ChatGPTAutomator()
    chatgpt.initialize(1)
    db = get_db()
    if chatgpt:
        try:
            now_datetime=datetime.now()
            chat_db_record = db.api_chats.insert_one({"created_at":now_datetime,"promt":input.promt,"status":"in_progress"})
            if not chatgpt.send_prompt_to_chatgpt(input.promt):
                db.api_chats.update_one({"_id":chat_db_record.inserted_id},{"$set":{"status":"failed","message":"send promt error (login page)"}})
                return JSONResponse(content={"answer":"1 hour limitation ."}, status_code=400)
                
            answer = chatgpt.return_last_response()
            try:
                answer=answer.split('json\nCopy\nEdit\n')[1]
            except:
                try:
                    answer=answer.split('json\nCopy\n')[1]
                except:
                    pass
                
                
            prompt_token = chatgpt.estimate_token_usage(input.promt)
            answer_token = chatgpt.estimate_token_usage(answer)
            chatgpt.driver.quit()
            db.api_chats.update_one({"_id":chat_db_record.inserted_id},{"$set":{"status":"complete", "response":answer, 'completion_tokens':answer_token+prompt_token,'prompt_tokens':prompt_token }})
            return JSONResponse(content={ "response":answer, 'completion_tokens':answer_token+prompt_token,'prompt_tokens':prompt_token }, status_code=200)
        except: 
            pass
        
        db.api_chats.update_one({"_id":chat_db_record.inserted_id},{"$set":{"status":"failed","message":"error in create chatgpt session"}})
        return JSONResponse(content={"answer":"error in create chatgpt session"}, status_code=400)
    else:
        print("failed")
        exit(0)



# @app.post("/quit/")
# async def quit(current_user: dict = Depends(get_current_user)):
#     user_id = str(current_user.get('_id'))
#     try:
#         chatgpt = chatgpt_session_manager.get_session(user_id)
#         chatgpt.quit()
#         return JSONResponse(content={"msg":"chatgpt session quited"}, status_code=200)
#     except:
#         return JSONResponse(content={"msg":"you dont have any chatgpt session ."}, status_code=400)
