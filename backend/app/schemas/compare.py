from pydantic import BaseModel, Field


class CompareRequest(BaseModel):
    document_id_a: int = Field(gt=0)
    document_id_b: int = Field(gt=0)


class CompareResponse(BaseModel):
    document_id_a: int
    document_id_b: int
    document_a_title: str
    document_b_title: str
    comparison: str
