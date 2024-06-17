# auth.py
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel
from db import get_database


async def get_db_instance():
    database = await get_database()
    return database

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

fake_users_db = {
    "user": {
        "username": "user",
        "full_name": "user Doe",
        "email": "user@example.com",
        "hashed_password": "user",
    },
    "user1": {
        "username": "admin",
        "full_name": "user1 Doe",
        "email": "user1@example.com",
        "hashed_password": "user1",
    }
}

class Token(BaseModel):
    access_token: str
    token_type: str

class UserInRequest(BaseModel):
    username: str
    password: str

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def authenticate_user(db, username: str, password: str):
    user = db.user_data.find_one({"username": username})
    if not user or user["hashed_password"] != password:
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(db, token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.user_data.find_one({"username": username})
    if user is None:
        raise credentials_exception
    return user