from pydantic import BaseModel


class DocumentSummaryResponse(BaseModel):
    document_id: int
    title: str
    summary: str
