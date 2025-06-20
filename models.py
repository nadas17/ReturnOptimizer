# models.py dosyası

from pydantic import BaseModel
from typing import List
import uuid

class ReturnRequest(BaseModel):
    user_id: uuid.UUID
    product_id: str
    message: str

class AnalysisResult(BaseModel):
    category: List[str]
    sentiment: float
    summary: str