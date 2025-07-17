#!/bin/bash
set -e

# Usage check
if [ $# -lt 3 ]; then
  echo "Usage: $0 <document_id> <top_k> <question>"
  echo "Example: $0 476782de-a8d7-4659-8de2-76dd9fe13ab9 3 \"apa itu RAG?\""
  exit 1
fi

DOC_ID="$1"
TOP_K="$2"
shift 2
QUESTION="$*"

echo "🔍 Retrieving top ${TOP_K} fragments for:"
echo "   • document_id = ${DOC_ID}"
echo "   • question    = \"${QUESTION}\""
echo

# Perform request with proper URL–encoding
RESPONSE=$(curl -s --get \
  --data-urlencode "document_id=${DOC_ID}" \
  --data-urlencode "question=${QUESTION}" \
  --data-urlencode "top_k=${TOP_K}" \
  http://localhost:8081/retrieve)

# Pretty‑print JSON if jq is available, otherwise raw
if command -v jq >/dev/null 2>&1; then
  echo "$RESPONSE" | jq .
else
  echo "$RESPONSE"
fi
