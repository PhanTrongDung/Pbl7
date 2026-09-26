from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DocumentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    law_type: str = Field(min_length=1, max_length=100)
    issue_date: datetime | None = None
    effective_date: datetime | None = None
    source_url: str | None = Field(default=None, max_length=500)
    file_path: str | None = Field(default=None, max_length=500)
    content: str | None = None


class DocumentOut(DocumentCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)
