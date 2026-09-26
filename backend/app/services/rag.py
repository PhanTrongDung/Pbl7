from typing import Any

from app.services.llm import generate_grounded_answer
from app.services.vector_store import search_chunks


def answer_question(question: str, limit: int = 3) -> tuple[str, list[str]]:
    results: list[dict[str, Any]] = search_chunks(question, limit)
    if not results:
        return (
            "Không tìm thấy đoạn văn bản pháp luật phù hợp trong kho dữ liệu. ",
            [],
        )

    excerpts = []
    citations = []
    for result in results:
        excerpt = str(result.get("content", "")).strip()
        if not excerpt:
            continue
        excerpts.append(excerpt)
        source = result.get("title") or f"Document {result['document_id']}"
        law_type = result.get("law_type")
        if law_type:
            source = f"{source} ({law_type})"
        citations.append(
            f"{source}, chunk {result['chunk_index']} "
            f"(score={result['score']:.3f})"
        )

    if not excerpts:
        return "Không tìm thấy nội dung pháp luật phù hợp.", []

    context = "\n\n".join(excerpts)
    try:
        answer = generate_grounded_answer(question, context)
    except Exception:
        answer = None
    if not answer:
        answer = "Dựa trên các đoạn văn bản được truy xuất:\n\n" + context
    return answer, citations
