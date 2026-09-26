from pydantic import BaseModel, ConfigDict


class ChunkOut(BaseModel):
    id: int
    document_id: int
    chunk_index: int
    content: str

    model_config = ConfigDict(from_attributes=True)


class ProcessDocumentResponse(BaseModel):
    document_id: int
    chunks_created: int
