from indexer.es_indexer import es, ES_INDEX

def retrieve(doc_id: str, query: str, top_k: int = 5) -> List[str]:
    body = {
        "size": top_k,
        "query": {
            "bool": {
                "must": [{"term": {"doc_id": doc_id}}],
                "should": [{"match": {"chunk": {"query": query}}}],
            }
        },
    }
    res = es.search(index=ES_INDEX, body=body)
    return [hit["_source"]["chunk"] for hit in res["hits"]["hits"]]