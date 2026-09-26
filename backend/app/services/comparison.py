from app.services.llm import generate_grounded_answer


def compare_texts(
    title_a: str,
    content_a: str,
    title_b: str,
    content_b: str,
) -> str:
    context = (
        f"VĂN BẢN A - {title_a}\n{content_a[:12000]}\n\n"
        f"VĂN BẢN B - {title_b}\n{content_b[:12000]}"
    )
    question = (
        f"So sánh {title_a} và {title_b}. Nêu các điểm giống nhau, khác nhau "
        "và thay đổi đáng chú ý. Chỉ sử dụng nội dung trong context."
    )
    try:
        answer = generate_grounded_answer(question, context)
    except Exception:
        answer = None
    if answer:
        return answer

    return (
        "Chưa cấu hình Gemini. Dữ liệu hiện có để so sánh: "
        f"{title_a} có {len(content_a)} ký tự; "
        f"{title_b} có {len(content_b)} ký tự. "
        "Hãy cấu hình GEMINI_API_KEY để nhận phân tích điểm giống và khác nhau."
    )
