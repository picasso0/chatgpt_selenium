from chatgpt_automatic import ChatGPTAutomator
from fastapi import FastAPI, HTTPException, Header,Query
from typing import Dict, List
from pydantic import BaseModel
import asyncio
import os
from time import sleep

chatgpt = ChatGPTAutomator()





app = FastAPI()


@app.post("/chat/")
async def chat(question:str=Query("")):
    breakpoint()
    if question==None or question=="":
        return "enter a message"

    chatgpt.send_prompt_to_chatgpt(question)
    answer = chatgpt.return_last_response()

    return {"answer":answer}

