# auth.py
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from global_vars import AUTH_JWT_SECRET_KEY, AUTH_JWTALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="توکن شما منقضی شده است",
        headers={"WWW-Authenticate": "Bearer"},
    )
    wrong_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="توکن شما صحیح نمیباشد",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, AUTH_JWT_SECRET_KEY, algorithms=[AUTH_JWTALGORITHM])
    except:
        raise wrong_exception
    try:
        user_id = payload.get('user_id')
        if user_id is None:
            raise credentials_exception
        return user_id
    except:
        raise credentials_exception
