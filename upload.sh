#!/bin/bash
set -e

if [ $# -ne 1 ]; then
  echo "Usage: $0 <filename>"
  exit 1
fi
FILE="$1"
[ -f "$FILE" ] || { echo "File '$FILE' tidak ditemukan"; exit 1; }

# 1. Upload
echo "➡️ Uploading '$FILE'..."
RESP=$(curl -s -F "file=@${FILE}" http://localhost:8081/upload)
echo "Raw response: $RESP"
DOC_ID=$(echo "$RESP" | sed -E 's/.*"document_id":"([^"]+)".*/\1/')
echo "✅ document_id: $DOC_ID"

#curl -s -X POST http://localhost:9200/rag_docs/_refresh

# 2. Hitung chunk
echo "🔍 Menghitung jumlah chunk..."
ES_COUNT=$(curl -s -XGET 'http://localhost:9200/rag_docs/_count' \
  -H 'Content-Type: application/json' \
  -d "{\"query\":{\"term\":{\"doc_id\":\"${DOC_ID}\"}}}" \
  | sed -E 's/.*\"count\":([0-9]+).*/\1/')

echo "✅ Jumlah chunk: $ES_COUNT"
echo
echo "🎉 Upload & indexing selesai!"
echo "   • document_id = $DOC_ID"
echo "   • chunk_count  = $ES_COUNT"
