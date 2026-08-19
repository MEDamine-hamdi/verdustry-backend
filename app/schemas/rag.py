from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from pydantic import ConfigDict

class ChatMessage(BaseModel):
    role: str  # "user" ou "assistant"
    content: str


class ChatRequest(BaseModel):
    companyId: int
    message: str
    history: Optional[List[ChatMessage]] = None


class ChatResponse(BaseModel):
    answer: str
    sources: Optional[List[str]] = None


class IngestRegulatoryRequest(BaseModel):
    sourceRef: str
    text: str


class IngestResponse(BaseModel):
    chunksCreated: int

class ChatMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    role: str
    content: str
    sources: Optional[List[dict]] = None
    createdAt: Optional[datetime] = None