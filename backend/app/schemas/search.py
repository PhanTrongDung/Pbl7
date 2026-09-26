from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(min_length=2)
    limit: int = Field(default=5, ge=1, le=20)


class SearchResult(BaseModel):
    score: float
    document_id: int
    chunk_id: int
    chunk_index: int
    content: str
    title: str | None = None
    law_type: str | None = None
