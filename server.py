import os
import re
import uuid
from typing import List, Dict, Any

from fastapi import FastAPI, UploadFile, File, HTTPException
from PyPDF2 import PdfReader
from docx import Document
from pptx import Presentation
from elasticsearch import Elasticsearch, ApiError

app = FastAPI(title="RAGPrabu Scored‐Retrieve API", version="0.1.0")

# Elasticsearch configuration
ES_HOST = os.getenv("ES_HOST", "http://localhost:9200")
ES_INDEX = "rag_docs"
es: Elasticsearch

@app.on_event("startup")
def startup_event():
    global es
    es = Elasticsearch(hosts=[ES_HOST])
    try:
        if not es.indices.exists(index=ES_INDEX):
            es.indices.create(
                index=ES_INDEX,
                body={
                    "settings": {
                        "similarity": {"default": {"type": "BM25"}}
                    },
                    "mappings": {
                        "properties": {
                            "doc_id": {"type": "keyword"},
                            "chunk": {"type": "text"}
                        }
                    }
                }
            )
    except ApiError as e:
        print(f"Warning: cannot create index '{ES_INDEX}': {e}")

@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}

def extract_text(path: str, ext: str) -> str:
    if ext == "pdf":
        reader = PdfReader(path)
        return "\n".join(p.extract_text() or "" for p in reader.pages)
    if ext in ("docx", "doc"):
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs)
    if ext in ("pptx", "ppt"):
        prs = Presentation(path)
        texts = []
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    t = shape.text.strip()
                    if t:
                        texts.append(t)
        return "\n".join(texts)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def chunk_text_semantic(
    text: str,
    max_words: int = 50,
    overlap_words: int = 20
) -> List[str]:
    sentences = re.split(r'(?<=[\.\?\!])\s+', text)
    chunks: List[str] = []
    current: List[str] = []
    count = 0
    for sent in sentences:
        words = sent.split()
        if count + len(words) > max_words and current:
            chunks.append(" ".join(current))
            current = current[-overlap_words:]
            count = len(current)
        current.extend(words)
        count += len(words)
    if current:
        chunks.append(" ".join(current))
    return chunks

@app.post("/upload")
async def upload(file: UploadFile = File(...)) -> Dict[str, Any]:
    name, ext = file.filename.rsplit(".", 1)
    ext = ext.lower()
    if ext not in ("pptx","ppt","docx","doc","pdf","txt","json","py"):
        raise HTTPException(415, f"Unsupported file type: .{ext}")

    doc_id = str(uuid.uuid4())
    tmp = f"/tmp/{doc_id}.{ext}"
    with open(tmp, "wb") as f:
        f.write(await file.read())
    raw = extract_text(tmp, ext)
    os.remove(tmp)

    frags = chunk_text_semantic(raw, max_words=50, overlap_words=20)
    for i, chunk in enumerate(frags):
        try:
            es.index(
                index=ES_INDEX,
                id=f"{doc_id}_{i}",
                body={"doc_id": doc_id, "chunk": chunk}
            )
        except ApiError as e:
            print(f"Warning: failed to index chunk {i}: {e}")

    try:
        es.indices.refresh(index=ES_INDEX)
    except ApiError:
        pass

    return {"document_id": doc_id, "chunk_count": len(frags)}

@app.get("/retrieve")
def retrieve(
    document_id: str,
    question: str,
    top_k: int = 5
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Retrieve top_k chunks matching `question`, returning each chunk with its BM25 score.
    """
    body = {
        "size": top_k,
        "query": {
            "bool": {
                "must": [
                    {"term": {"doc_id": document_id}},
                    {"match": {"chunk": {"query": question}}}
                ]
            }
        }
    }
    try:
        res = es.search(index=ES_INDEX, body=body)
    except ApiError as e:
        raise HTTPException(500, f"Search error: {e}")

    results = []
    for hit in res["hits"]["hits"]:
        results.append({
            "chunk": hit["_source"]["chunk"],
            "score": hit["_score"]
        })

    return {"fragments": results}
