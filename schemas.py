from pydantic import BaseModel

class Question(BaseModel):
    question: str
    
class Token(BaseModel):
    access_token: str
    token_type: str

class UserInRequest(BaseModel):
    username: str
    password: str