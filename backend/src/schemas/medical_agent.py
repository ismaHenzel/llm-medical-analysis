from typing import List

from pydantic import BaseModel


class ChatRequest(BaseModel):
    thread_id: int
    message: str
    patient_record: dict

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatHistoryResponse(BaseModel):
    messages: List[ChatMessage]
