from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.database.session import get_db
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.user import User
from app.schemas.chunk import ChunkOut, ProcessDocumentResponse
from app.schemas.compare import CompareRequest, CompareResponse
from app.schemas.document import DocumentCreate, DocumentOut
from app.schemas.summary import DocumentSummaryResponse
from app.services.chunking import chunk_text
from app.services.comparison import compare_texts
from app.services.llm import generate_grounded_answer
from app.services.vector_store import index_chunks
from app.services.pdf import extract_pdf_text

router = APIRouter(prefix="/documents", tags=["documents"])
PDF_STORAGE = Path(__file__).resolve().parents[4] / "data" / "pdf"


def parse_optional_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"Invalid date: {value}") from exc


@router.post("", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
def create_document(
    payload: DocumentCreate,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = Document(**payload.model_dump())
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@router.post("/upload", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    law_type: str = Form(...),
    issue_date: str | None = Form(default=None),
    effective_date: str | None = Form(default=None),
    source_url: str | None = Form(default=None),
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    PDF_STORAGE.mkdir(parents=True, exist_ok=True)
    stored_path = PDF_STORAGE / f"{uuid4().hex}.pdf"
    stored_path.write_bytes(await file.read())

    try:
        content = extract_pdf_text(stored_path)
    except ModuleNotFoundError as exc:
        stored_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=503,
            detail="PyMuPDF is not installed. Run: python -m pip install PyMuPDF",
        ) from exc
    except Exception as exc:
        stored_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="Could not extract PDF text") from exc

    document = Document(
        title=title,
        law_type=law_type,
        issue_date=parse_optional_datetime(issue_date),
        effective_date=parse_optional_datetime(effective_date),
        source_url=source_url,
        file_path=str(stored_path),
        content=content,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@router.get("", response_model=list[DocumentOut])
def list_documents(
    law_type: str | None = Query(default=None),
    search: str | None = Query(default=None, min_length=1),
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = select(Document).order_by(Document.id.desc())
    if law_type:
        query = query.where(Document.law_type == law_type)
    if search:
        query = query.where(Document.title.ilike(f"%{search}%"))
    return db.scalars(query).all()


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(
    document_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.post("/{document_id}/process", response_model=ProcessDocumentResponse)
def process_document(
    document_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    if not document.content:
        raise HTTPException(status_code=422, detail="Document has no extracted content")

    db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == document_id))
    chunks = [
        DocumentChunk(document_id=document_id, chunk_index=index, content=content)
        for index, content in enumerate(chunk_text(document.content))
    ]
    db.add_all(chunks)
    db.commit()
    return ProcessDocumentResponse(document_id=document_id, chunks_created=len(chunks))


@router.get("/{document_id}/chunks", response_model=list[ChunkOut])
def list_document_chunks(
    document_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if db.get(Document, document_id) is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return db.scalars(
        select(DocumentChunk)
        .where(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index)
    ).all()


@router.post("/{document_id}/index")
def index_document(
    document_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if db.get(Document, document_id) is None:
        raise HTTPException(status_code=404, detail="Document not found")
    chunks = db.scalars(
        select(DocumentChunk).where(DocumentChunk.document_id == document_id)
    ).all()
    indexed = index_chunks(
        [
            {
                "id": chunk.id,
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "title": document.title,
                "law_type": document.law_type,
            }
            for chunk in chunks
        ]
    )
    return {"document_id": document_id, "chunks_indexed": indexed}


@router.post("/{document_id}/summary", response_model=DocumentSummaryResponse)
def summarize_document(
    document_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    if not document.content:
        raise HTTPException(status_code=422, detail="Document has no content to summarize")

    chunks = db.scalars(
        select(DocumentChunk)
        .where(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index)
        .limit(12)
    ).all()
    context = "\n\n".join(chunk.content for chunk in chunks)
    if not context:
        context = document.content[:14000]

    try:
        summary = generate_grounded_answer(
            f"Hãy tóm tắt văn bản pháp luật có tiêu đề: {document.title}",
            context,
        )
    except Exception:
        summary = None
    if not summary:
        summary = "Tóm tắt dựa trên nội dung văn bản:\n\n" + context[:4000]

    return DocumentSummaryResponse(
        document_id=document.id,
        title=document.title,
        summary=summary,
    )


@router.post("/compare", response_model=CompareResponse)
def compare_documents(
    payload: CompareRequest,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.document_id_a == payload.document_id_b:
        raise HTTPException(status_code=422, detail="Documents must be different")

    document_a = db.get(Document, payload.document_id_a)
    document_b = db.get(Document, payload.document_id_b)
    if document_a is None or document_b is None:
        raise HTTPException(status_code=404, detail="One or both documents not found")
    if not document_a.content or not document_b.content:
        raise HTTPException(status_code=422, detail="Both documents must have content")

    comparison = compare_texts(
        document_a.title,
        document_a.content,
        document_b.title,
        document_b.content,
    )
    return CompareResponse(
        document_id_a=document_a.id,
        document_id_b=document_b.id,
        document_a_title=document_a.title,
        document_b_title=document_b.title,
        comparison=comparison,
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(document)
    db.commit()
