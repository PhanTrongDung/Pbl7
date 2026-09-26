from datetime import datetime
from pathlib import Path

from sqlalchemy import select

from app.database.session import SessionLocal
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.chunking import chunk_text
from app.services.pdf import extract_pdf_text
from app.services.vector_store import index_chunks

PDF_DIR = Path(__file__).resolve().parents[1] / "data" / "pdf"
PDF_NAME = "VanBanGoc_BO LUAT 45 QH14.pdf"


def main() -> None:
    pdf_path = PDF_DIR / PDF_NAME
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    content = extract_pdf_text(pdf_path)
    if not content:
        raise ValueError("The PDF contains no extractable text")

    with SessionLocal() as db:
        document = db.scalar(select(Document).where(Document.file_path == str(pdf_path)))
        if document is None:
            document = Document(
                title="Bộ luật Lao động 2019",
                law_type="Lao động",
                issue_date=datetime(2019, 11, 20),
                effective_date=datetime(2021, 1, 1),
                source_url="https://vbpl.vn/",
                file_path=str(pdf_path),
                content=content,
            )
            db.add(document)
            db.flush()
        else:
            document.content = content
            db.execute(
                DocumentChunk.__table__.delete().where(
                    DocumentChunk.document_id == document.id
                )
            )

        chunks = [
            DocumentChunk(document_id=document.id, chunk_index=index, content=text)
            for index, text in enumerate(chunk_text(content))
        ]
        db.add_all(chunks)
        db.commit()
        db.refresh(document)
        db.refresh(chunks[0])

        indexed = index_chunks(
            [
                {
                    "id": chunk.id,
                    "document_id": document.id,
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                    "title": document.title,
                    "law_type": document.law_type,
                }
                for chunk in chunks
            ]
        )

    print(f"Document ID: {document.id}")
    print(f"Extracted characters: {len(content)}")
    print(f"Chunks created: {len(chunks)}")
    print(f"Chunks indexed: {indexed}")


if __name__ == "__main__":
    main()
