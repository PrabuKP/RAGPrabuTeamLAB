#!/usr/bin/env bash
set -euo pipefail

API_IMAGE="ragprabu-backend:latest"
API_NAME="ragprabu-api"
ES_NAME="es"
NETWORK="ragnet"
HOST_API_PORT=8081
CTR_API_PORT=8081

# 1. Buat network ragnet
if ! docker network ls --format '{{.Name}}' | grep -q "^${NETWORK}\$"; then
  echo "🌐 Membuat Docker network '${NETWORK}'..."
  docker network create "${NETWORK}"
fi

# 2. Restart Elasticsearch
echo "🛑 Stop & remove container '${ES_NAME}' jika ada..."
if docker ps -a --format '{{.Names}}' | grep -q "^${ES_NAME}\$"; then
  docker stop "${ES_NAME}" && docker rm "${ES_NAME}"
fi
echo "🚀 Menjalankan Elasticsearch di network '${NETWORK}'..."
docker run -d --name "${ES_NAME}" \
  --network "${NETWORK}" \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  docker.elastic.co/elasticsearch/elasticsearch:8.6.2

# 3. Build ulang API image
echo "🔨 Building Docker image ${API_IMAGE}..."
docker build --no-cache -t "${API_IMAGE}" .

# 4. Restart API container
echo "🛑 Stop & remove container '${API_NAME}' jika ada..."
if docker ps -a --format '{{.Names}}' | grep -q "^${API_NAME}\$"; then
  docker stop "${API_NAME}" && docker rm "${API_NAME}"
fi

echo "🚀 Menjalankan API container di network '${NETWORK}' (host ${HOST_API_PORT} → container ${CTR_API_PORT})..."
docker run -d --name "${API_NAME}" \
  --network "${NETWORK}" \
  -p ${HOST_API_PORT}:${CTR_API_PORT} \
  -e ES_HOST="http://${ES_NAME}:9200" \
  "${API_IMAGE}"

# 5. Tunggu API siap
echo
echo "⏳ Menunggu API siap di http://localhost:${HOST_API_PORT}/health..."
for i in {1..10}; do
  if curl -s http://localhost:${HOST_API_PORT}/health >/dev/null; then
    echo "✅ API OK!"
    break
  fi
  echo "   - retry $i..."
  sleep 1
done

# 6. Cek final
echo
echo "🔍 Final check:"
curl -s http://localhost:${HOST_API_PORT}/health && echo

echo
echo "✅ Deployment complete!"
echo "   • Elasticsearch: http://localhost:9200"
echo "   • API health:   http://localhost:${HOST_API_PORT}/health"
