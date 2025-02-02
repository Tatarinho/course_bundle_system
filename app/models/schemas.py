from pydantic import BaseModel
from typing import Dict

class TeacherRequest(BaseModel):
    topics: Dict[str, int]


class Quote(BaseModel):
    provider: str
    price: float
