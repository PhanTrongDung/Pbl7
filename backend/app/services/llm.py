from app.config.settings import settings


def generate_grounded_answer(question: str, context: str) -> str | None:
    if not settings.gemini_api_key:
        return None

    import google.generativeai as genai

    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel(settings.gemini_model)
    prompt = f"""
Bạn là trợ lý pháp lý Việt Nam. Chỉ trả lời dựa trên CONTEXT bên dưới.
Nếu CONTEXT không đủ để kết luận, hãy nói rõ là chưa đủ dữ liệu.
Không tự suy diễn, không bịa điều luật, không đưa tư vấn chắc chắn thay cho luật sư.
Trả lời bằng tiếng Việt, ngắn gọn và nêu rõ căn cứ từ context.

QUESTION:
{question}

CONTEXT:
{context}
""".strip()
    response = model.generate_content(prompt)
    answer = getattr(response, "text", None)
    return answer.strip() if answer else None
