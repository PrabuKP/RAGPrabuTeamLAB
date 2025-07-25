# RAGPrabu

## Description
RAGPrabu is a backend API server for Retrieval‑Augmented Generation (RAG) that:
1. Accepts multiple document formats: PDF, DOCX, PPTX, TXT, JSON, PY.
2. Extracts raw text and splits it into searchable fragments (chunks).
3. Indexes those fragments into Elasticsearch using the BM25 algorithm.
4. Exposes an endpoint to retrieve the top‑k most relevant fragments for any user query.

By combining document retrieval with generative AI, RAGPrabu delivers real‑time, fact‑based answers that are both accurate and transparent.

---

## Key Features
- **File Upload**:
  - `POST /upload` for multipart-form file uploads (shell scripts, client.py).
  - `POST /upload-from-data` for selecting files in the `Data/` folder (UI).
- **Chunking**:
  - Uses llama‑index’s `TokenTextSplitter` to create ~300-word chunks with 50-word overlap.
- **Indexing**:
  - Stores fragments in Elasticsearch with BM25 as the similarity algorithm.
- **Retrieval**:
  - `GET /retrieve` returns fragments plus their BM25 scores.
- **Health Check**:
  - `GET /health` → `{"status":"ok"}`.
- **Simple Web UI**:
  - Static `index.html` under `static/` for upload & retrieval without writing code.

---

## Prerequisites
- **Docker** (and Docker Compose, optional)
- **Python 3.10** (if running locally without Docker)
- A Docker network named `ragnet` (created automatically by the `deploy.sh` script)
- Default ports:
  - Elasticsearch → `9200`
  - FastAPI → `8081`

---

## Project Structure
```
RAGPrabu/
├── Dockerfile
├── deploy.sh
├── upload.sh
├── retrieve.sh
├── requirements.txt
├── server.py
├── client.py
├── static/              # index.html, CSS, JS for the UI
├── Data/                # sample documents
└── README.md            # this file
```

---

## Installation & Build

### Using Docker
```bash
git clone https://github.com/PrabuKP/RAGPrabuTeamLAB.git
cd RAGPrabuTeamLAB

# 1. Build the API image
docker build -t ragprabu-backend:latest .

# 2. Run everything via deploy.sh
chmod +x deploy.sh
./deploy.sh
```

`deploy.sh` will:
1. Create Docker network `ragnet` if missing
2. Restart Elasticsearch container (`es`) in `ragnet`
3. Build the API image
4. Restart the `ragprabu-api` container on `:8081`

### Without Docker (Local)
```bash
# 1. Create & activate virtualenv
python3.10 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start Elasticsearch externally on port 9200

# 4. Launch FastAPI
uvicorn server:app --host 0.0.0.0 --port 8081 --reload
```

### Using Image (If Your Are Using Windows Operating System, Use this step)
```bash
# 1. Download From Google Drive and Load the image.
docker load -i ragprabu-backend.tar
docker load -i elasticsearch-8.6.2.tar

# Example
docker load -i "C:\Users\prabu\Documents\2025\elasticsearch-8.6.2.tar"

#2. Or Pull from dockerhub using
docker pull prabukp/ragprabu-backend:latest
```


```bash
# 2. After you load the image, Run Your Image Using this command
# For Elasticsearch
docker run -d --name es `
  -p 9200:9200 `
  -e "discovery.type=single-node" `
  -e "xpack.security.enabled=false" `
  docker.elastic.co/elasticsearch/elasticsearch:8.6.2


# For RAG
docker network create ragnet
docker network connect ragnet es

docker run -d --name ragprabu-api `
  --network ragnet `
  -p 8081:8081 `
  -e ES_HOST="http://es:9200" `
  ragprabu-backend:latest

```
---

## Usage

### Health Check
```bash
curl http://localhost:8081/health
# → {"status":"ok"}
```

### Upload and Retrieve via Shell Script
```bash
#1. Upload Your Document
chmod +x upload.sh
./upload.sh Data/sample.txt

#1. Retrieve
./retrieve.sh “Document ID” “Number of K” "Question"

#Example
./retrieve.sh 22a2fdfe-b960-4dab-80a9-4a8e17c3aa95 3 "RAG Definition?"
```

### Upload and Retrieve via Web UI
1. Open your browser to `http://localhost:8081/`.
2. Select a file from the dropdown (files in `Data/`), click **Upload**.
3. Select document id, enter the number of k and the question you want to ask.

### Upload and Retrieve via Python Script
```bash
#Use this command
python3 client.py DirectoryFolder FileName TotalK "Question"

#Example
python3 client.py Data pdf-sample.pdf 3 "RAG Definition?"
```

### Python Client Example (`client.py`)
```python
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

```

---

## Troubleshooting
- **Connection Refused on 8081**:
  - Ensure the `ragprabu-api` container is running:
    ```bash
    docker ps | grep ragprabu-api
    ```
- **Media Type Errors in ES**:
  - Make sure Elasticsearch launches with security disabled:
    ```bash
    docker run -d --name es --network ragnet -p 9200:9200       -e discovery.type=single-node -e xpack.security.enabled=false       docker.elastic.co/elasticsearch/elasticsearch:8.6.2
    ```
- **Import Errors for llama-index**:
  - Verify `llama-index` version in `requirements.txt` matches your code imports.

---

## License
Prabu Kresna Putra | PRSDI - BRIN © 2025

<sub>Generated on July, 2025</sub>
