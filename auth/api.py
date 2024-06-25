
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from auth.auth import (
    authenticate_bot,
    create_access_token,
)
from auth.schema import BotInRequest, Token

app = APIRouter()

@app.post("/token", response_model=Token)
async def login_for_access_token(input: BotInRequest):
    user = await authenticate_bot(input.username, input.password)
    if not user:
        credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
        raise credentials_exception
        
        
    access_token = create_access_token(data={"sub": user["username"]})
    return JSONResponse(content={"access_token": access_token, "token_type": "bearer"}, status_code=200)
