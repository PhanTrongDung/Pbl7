from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.database.session import get_db
from app.models.chat_history import ChatHistory
from app.models.user import User
from app.schemas.chat import ChatHistoryItem, ChatRequest, ChatResponse
from app.schemas.search import SearchRequest, SearchResult
from app.services.rag import answer_question
from app.services.vector_store import search_chunks

router = APIRouter()


@router.get("/chat/history", response_model=list[ChatHistoryItem])
def get_chat_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.scalars(
        select(ChatHistory)
        .where(ChatHistory.user_id == current_user.id)
        .order_by(ChatHistory.created_at.desc())
    ).all()


@router.post("/chat", response_model=ChatResponse)
def chat_with_legal_ai(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        answer, citations = answer_question(payload.question)
    except ModuleNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail="RAG dependencies are not installed. Run: python -m pip install -r requirements.txt",
        ) from exc
    db.add(
        ChatHistory(
            user_id=current_user.id,
            question=payload.question,
            answer=answer,
        )
    )
    db.commit()
    return ChatResponse(
        answer=answer,
        citations=citations,
    )


@router.post("/search", response_model=list[SearchResult])
def search_legal_docs(
    payload: SearchRequest,
    _: User = Depends(get_current_user),
):
    return search_chunks(payload.query, payload.limit)


@router.post("/sync-laws")
def sync_laws():
    return {"message": "Sync API ready"}
