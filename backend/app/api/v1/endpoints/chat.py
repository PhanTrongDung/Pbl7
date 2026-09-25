from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat_with_legal_ai(payload: ChatRequest):
    return ChatResponse(
        answer=f"Câu hỏi của bạn: {payload.question}. Hệ thống RAG đang sẵn sàng xử lý và trích dẫn văn bản pháp luật liên quan.",
        citations=["Luật Lao động 2019", "Nghị định liên quan"],
    )


@router.post("/search")
def search_legal_docs():
    return {"message": "Search API ready"}


@router.post("/summary")
def summarize_document():
    return {"message": "Summary API ready"}


@router.post("/compare")
def compare_documents():
    return {"message": "Compare API ready"}


@router.post("/sync-laws")
def sync_laws():
    return {"message": "Sync API ready"}
