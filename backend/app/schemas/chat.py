from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    citations: list[str] = []


class ChatHistoryItem(BaseModel):
    id: int
    question: str
    answer: str

    class Config:
        from_attributes = True
