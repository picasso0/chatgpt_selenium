from pydantic import BaseModel
from typing import Optional

class Question(BaseModel):
    question: str
    
class Promt(BaseModel):
    promt: str
    type: str
    window_id: Optional[str]