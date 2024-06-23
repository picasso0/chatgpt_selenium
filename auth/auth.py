# auth.py
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from db import get_database
from global_vars import AUTH_JWT_SECRET_KEY, AUTH_JWTALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def authenticate_bot(username: str, password: str):
    db = await get_database()
    bot = await db.bots.find_one({"username": username})
    if not bot or bot["password"] != password:
        return False
    return bot

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=300)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, AUTH_JWT_SECRET_KEY, algorithm=AUTH_JWTALGORITHM)
    return encoded_jwt

async def get_current_bot(token: str = Depends(oauth2_scheme)):
    db = await get_database()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="توکن شما منقضی شده است",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, AUTH_JWT_SECRET_KEY, algorithms=[AUTH_JWTALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    bot = await db.bots.find_one({"username": username})
    if bot is None:
        raise credentials_exception
    return bot