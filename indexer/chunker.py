from typing import List

def chunk_text(text: str, size: int = 400, overlap: int = 50) -> List[str]:
    words = text.split()
    chunks: List[str] = []
    start = 0
    while start < len(words):
        end = start + size
        chunk = words[start:end]
        chunks.append(" ".join(chunk))
        start += size - overlap
    return chunks