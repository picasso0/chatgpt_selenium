from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

user_data = {}
class UserData:
    def __init__(self):
        self.data = {}
class UserDataMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        user_id = request.headers.get("X-User-ID")
        if user_id not in user_data:
            user_data[user_id] = UserData()

        request.state.user_data = user_data[user_id]
        response = await call_next(request)
        return response
    
app = FastAPI()
app.add_middleware(UserDataMiddleware)



@app.get("/data")
async def get_data(request: Request):
    user_data = request.state.user_data
    # Access and modify the user-specific data
    return user_data.data

@app.post("/data")
async def set_data(request: Request):
    user_data = request.state.user_data
    user_data.data = request.headers.get("X-User-ID")
    return {"message": "Data updated"}