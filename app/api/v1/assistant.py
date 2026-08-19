from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import require_role
from app.core.tenant import enforce_company_access
from app.models.user import User
from app.models.chat_message import ChatMessage
from app.repositories.chat_message_repository import ChatMessageRepository
from app.schemas.rag import (
    ChatRequest,
    ChatResponse,
    IngestRegulatoryRequest,
    IngestResponse,
    ChatMessageResponse,
)
from app.services.rag_service import RagService

router = APIRouter(prefix="/assistant", tags=["Assistant (RAG)"])


@router.get("/history", response_model=List[ChatMessageResponse])
def get_history(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "ESG_MANAGER", "EXECUTIVE", "AUDITOR")),
):
    enforce_company_access(current_user, company_id)
    repo = ChatMessageRepository(db)
    messages = repo.get_all_by_company(company_id)
    return [
        ChatMessageResponse(
            id=str(m.id),
            role=m.role,
            content=m.content,
            sources=m.sources,
            createdAt=m.created_at,
        )
        for m in messages
    ]


@router.post("/chat", response_model=ChatResponse)
def chat(
    data: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "ESG_MANAGER", "EXECUTIVE", "AUDITOR")),
):
    enforce_company_access(current_user, data.companyId)
    service = RagService(db)
    repo = ChatMessageRepository(db)

    history = [h.model_dump() for h in data.history] if data.history else None
    result = service.chat(data.companyId, data.message, history)

    repo.create(ChatMessage(
        company_id=data.companyId,
        user_id=current_user.id,
        role="user",
        content=data.message,
        sources=None,
    ))
    repo.create(ChatMessage(
        company_id=data.companyId,
        user_id=current_user.id,
        role="assistant",
        content=result["answer"],
        sources=result.get("sources"),
    ))

    return ChatResponse(**result)


@router.post("/ingest-regulatory", response_model=IngestResponse)
def ingest_regulatory(
    data: IngestRegulatoryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN")),
):
    service = RagService(db)
    count = service.ingest_regulatory_document(data.sourceRef, data.text)
    return IngestResponse(chunksCreated=count)


@router.post("/sync-company-data/{company_id}", response_model=IngestResponse)
def sync_company_data(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "ESG_MANAGER")),
):
    enforce_company_access(current_user, company_id)
    service = RagService(db)
    count = service.sync_company_data(company_id)
    return IngestResponse(chunksCreated=count)