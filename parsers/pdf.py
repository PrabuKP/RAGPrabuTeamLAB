from PyPDF2 import PdfReader

def extract_text(path: str) -> str:
    reader = PdfReader(path)
    lines = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            lines.append(text)
    return "\n".join(lines)