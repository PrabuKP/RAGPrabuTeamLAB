from elasticsearch import Elasticsearch

ES_INDEX = "rag_docs"
es: Elasticsearch | None = None

def init_es(host: str = "http://localhost:9200"):
    global es
    es = Elasticsearch(hosts=[host])
    if not es.indices.exists(index=ES_INDEX):
        es.indices.create(
            index=ES_INDEX,
            body={
                "settings": {"similarity": {"default": {"type": "BM25"}}},
                "mappings": {"properties": {"doc_id": {"type": "keyword"}, "chunk": {"type": "text"}}},
            },
        )

def index_chunks(doc_id: str, chunks: List[str]):
    for i, chunk in enumerate(chunks):
        es.index(index=ES_INDEX, id=f"{doc_id}_{i}", body={"doc_id": doc_id, "chunk": chunk})
