from typing import List, Dict, Any
from pydantic import BaseModel


class SqlPreviewRequest(BaseModel):
    connectionUrl: str
    query: str


class SqlPreviewResponse(BaseModel):
    rows: List[Dict[str, Any]]