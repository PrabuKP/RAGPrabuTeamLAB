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

---

## Usage

### Health Check
```bash
curl http://localhost:8081/health
# → {"status":"ok"}
```

### Upload via Shell Script
```bash
chmod +x upload.sh
./upload.sh Data/sample_long.txt
```

### Upload via Web UI
1. Open your browser to `http://localhost:8081/`.
2. Select a file from the dropdown (files in `Data/`), click **Upload**.

### Retrieve Chunks
```bash
chmod +x retrieve.sh
./retrieve.sh <DOCUMENT_ID> <TOP_K> "<QUESTION>"
# example:
./retrieve.sh 123e4567-e89b-12d3-a456-426614174000 5 "what is RAG?"
```
Or directly with curl:
```bash
curl "http://localhost:8081/retrieve?document_id=123e4567-e89b-12d3-a456-426614174000&question=what%20is%20RAG%3F&top_k=5"
```

### Python Client Example (`client.py`)
```python
from client import health, upload, retrieve

# 1. Health check
print(health())

# 2. Upload
res = upload("Data/sample_long.txt")
doc_id = res["document_id"]
print("Document ID:", doc_id)

# 3. Retrieve top‑3
out = retrieve(doc_id, "what is RAG?", top_k=3)
for frag in out["fragments"]:
    print(f"Score: {frag['score']:.3f} – {frag['chunk'][:80]}…")
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
MIT © 2025

<sub>Generated on July 21, 2025</sub>
