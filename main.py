from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from chatgpt.api import app as chatgpt_apis

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.include_router(chatgpt_apis)


