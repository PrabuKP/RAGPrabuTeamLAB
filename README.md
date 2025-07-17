# RAGPrabu Backend

**Deskripsi**  
Backend API untuk Retrieval‑Augmented Generation (RAG) dengan FastAPI, Elasticsearch, dan llama‑index.

**Struktur**  
- `server.py`: FastAPI app  
- `client.py`: contoh panggilan API  
- `parsers/`: modul ekstraksi teks  
- `indexer/`: chunking & indexing BM25 ke Elasticsearch  
- `retriever/`: modul retrieval fragmen  
- `Dockerfile`, `requirements.txt`: environment reproducible  

**Cara menjalankan**  
```bash
docker build -t ragprabu-backend:latest .
docker run -d --name es \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  docker.elastic.co/elasticsearch/elasticsearch:8.6.2

docker run -d --name ragprabu-api \
  --network host \
  -e ES_HOST=http://localhost:9200 \
  ragprabu-backend:latest
