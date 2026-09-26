from pathlib import Path
import os
import shutil


def extract_pdf_text(file_path: Path) -> str:
    import fitz

    with fitz.open(file_path) as document:
        pages = [page.get_text("text") for page in document]
        text = "\n\n".join(page.strip() for page in pages if page.strip()).strip()
        if text:
            return text

        try:
            import pytesseract
            from PIL import Image
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "Scanned PDF requires OCR. Install: python -m pip install pytesseract Pillow "
                "and install Tesseract OCR with Vietnamese language support."
            ) from exc

        tesseract_path = os.getenv("TESSERACT_CMD") or shutil.which("tesseract")
        common_paths = (
            Path("C:/Program Files/Tesseract-OCR/tesseract.exe"),
            Path("C:/Program Files (x86)/Tesseract-OCR/tesseract.exe"),
        )
        if not tesseract_path:
            tesseract_path = next(
                (str(path) for path in common_paths if path.exists()),
                None,
            )
        if not tesseract_path:
            raise RuntimeError(
                "Tesseract OCR is not installed. Run: "
                "winget install UB-Mannheim.TesseractOCR, then restart PowerShell."
            )
        pytesseract.pytesseract.tesseract_cmd = tesseract_path

        ocr_pages = []
        for page in document:
            pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            image = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
            ocr_pages.append(pytesseract.image_to_string(image, lang="vie+eng"))
        return "\n\n".join(page.strip() for page in ocr_pages if page.strip()).strip()
