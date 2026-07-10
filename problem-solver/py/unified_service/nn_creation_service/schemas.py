from pydantic import BaseModel
from typing import List, Dict, Any
class ModelSchema(BaseModel):
    model_name : str
    layers: List[Dict[str, Any]]

class AnswerSchema(BaseModel):
    session_id: str
    status: str
    comments: str
    model_name: str
    generated_code: str