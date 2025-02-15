from fastapi.responses import JSONResponse
from fastapi import APIRouter ,Depends, Body, HTTPException
from auth.auth import get_current_user
from chatgpt.schema import Question, Promt
from datetime import datetime
from chatgpt.chatgpt_manager import chatgpt_session_manager
# from chatgpt.chatgpt_automatic_proxy import ChatGPTAutomator
from chatgpt.chatgpt_automatic import ChatGPTAutomator
from db import get_db
from asyncio import create_task
from time import sleep
app = APIRouter()


@app.post("/sendPromt/")
async def send_prompt(input: Promt=Body()):
    gpt_type = input.type
    incognito = 1
    chatgpt = ChatGPTAutomator()
    await chatgpt.initialize(1)
    if chatgpt:
        try:
            now_datetime=datetime.now()
            if not chatgpt.send_prompt_to_chatgpt(input.promt):
                return JSONResponse(content={"answer":"1 hour limitation ."}, status_code=400)
                
            # if chatgpt.show_check_verify():
            #     return JSONResponse(content={"answer":"لطفا مجددا تلاش فرمایید خطای کپچا ."}, status_code=400)
        
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
            return JSONResponse(content={ "response":answer, 'completion_tokens':answer_token+prompt_token,'prompt_tokens':prompt_token }, status_code=200)
        except: 
            pass
    
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
