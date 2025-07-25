#!/usr/bin/env python3
import os
import sys
import requests
import json

BASE_URL = "http://localhost:8081"

def health() -> dict:
    """
    Check service health status.
    GET /health
    """
    resp = requests.get(f"{BASE_URL}/health")
    resp.raise_for_status()
    return resp.json()

def upload(file_path: str) -> dict:
    """
    Upload a document and return document_id and chunk_count.
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
    Retrieve top-k fragments for a given question and document_id.
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
    if len(sys.argv) != 5:
        print("Usage: python3 client.py <folder> <filename> <top_k> <question>")
        print('Example: python3 client.py Data sample.txt 3 "What is RAG?"')
        sys.exit(1)

    folder = sys.argv[1]
    filename = sys.argv[2]
    top_k = int(sys.argv[3])
    question = sys.argv[4]
    file_path = os.path.join(folder, filename)

    print("=== Health Check ===")
    print(json.dumps(health(), indent=2))

    print(f"\n=== Uploading: {file_path} ===")
    up = upload(file_path)
    doc_id = up["document_id"]
    chunk_count = up.get("chunk_count", "?")
    print(json.dumps(up, indent=2))

    print(f"\n=== Retrieving top {top_k} results for: '{question}' ===")
    ret = retrieve(doc_id, question, top_k=top_k)
    print(json.dumps(ret, indent=2))  # ✅ Print full JSON like retrieve.sh

if __name__ == "__main__":
    main()
