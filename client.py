#!/usr/bin/env python3
import os
import sys
import requests

BASE_URL = "http://localhost:8081"

def health() -> dict:
    """
    Cek status service.
    GET /health
    """
    resp = requests.get(f"{BASE_URL}/health")
    resp.raise_for_status()
    return resp.json()

def upload(file_path: str) -> dict:
    """
    Upload dokumen dan dapatkan document_id & chunk_count.
    POST /upload
    """
    if not os.path.isfile(file_path):
        print(f"Error: file not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    with open(file_path, "rb") as f:
        files = {"file": (os.path.basename(file_path), f)}
        resp = requests.post(f"{BASE_URL}/upload", files=files)
    resp.raise_for_status()
    return resp.json()

def retrieve(document_id: str, question: str, top_k: int = 5) -> dict:
    """
    Ambil top-k fragmen untuk sebuah pertanyaan pada document_id.
    GET /retrieve?document_id=…&question=…&top_k=…
    """
    params = {
        "document_id": document_id,
        "question": question,
        "top_k": top_k
    }
    resp = requests.get(f"{BASE_URL}/retrieve", params=params)
    resp.raise_for_status()
    return resp.json()

def main():
    print("=== Health Check ===")
    print(health())

    # Contoh upload
    sample = "sample.txt"
    print(f"\n=== Upload '{sample}' ===")
    up = upload(sample)
    doc_id = up["document_id"]
    chunk_count = up.get("chunk_count", "?")
    print(f"document_id = {doc_id}")
    print(f"chunk_count  = {chunk_count}")

    # Contoh retrieve
    question = "apa itu RAG?"
    k = 3
    print(f"\n=== Retrieve top {k} for question: {question!r} ===")
    ret = retrieve(doc_id, question, top_k=k)
    for i, frag in enumerate(ret.get("fragments", []), 1):
        # jika server juga mengembalikan skor, tampilkan skor
        score = frag.get("score")
        chunk = frag.get("chunk")
        if score is not None:
            print(f"{i}. [score={score:.3f}] {chunk[:80]}{'…' if len(chunk)>80 else ''}")
        else:
            print(f"{i}. {chunk[:80]}{'…' if len(chunk)>80 else ''}")

if __name__ == "__main__":
    main()
