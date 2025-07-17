#!/bin/bash
set -e

# 1. Buat network 'ragnet' jika belum ada
if ! docker network ls --format '{{.Name}}' | grep -q '^ragnet$'; then
  echo "🌐 Membuat Docker network 'ragnet'..."
  docker network create ragnet
fi

# 2. Restart Elasticsearch container
echo "🛑 Stop & remove container 'es' jika ada..."
if docker ps -a --format '{{.Names}}' | grep -q '^es$'; then
  docker stop es
  docker rm es
fi

echo "🚀 Menjalankan Elasticsearch di network 'ragnet'..."
docker run -d --name es \
  --network ragnet \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  docker.elastic.co/elasticsearch/elasticsearch:8.6.2

# 3. Build ulang API image
echo "🔨 Building Docker image ragprabu-backend:latest..."
docker build --no-cache -t ragprabu-backend:latest .

# 4. Restart API container
echo "🛑 Stop & remove container 'ragprabu-api' jika ada..."
if docker ps -a --format '{{.Names}}' | grep -q '^ragprabu-api$'; then
  docker stop ragprabu-api
  docker rm ragprabu-api
fi

echo "🚀 Menjalankan API container di network 'ragnet' (port 8081)..."
docker run -d --name ragprabu-api \
  --network ragnet \
  -p 8081:8081 \
  -e ES_HOST=http://es:9200 \
  ragprabu-backend:latest

# 5. Cek status Elasticsearch via network ragnet
echo
echo "🔍 Mengecek Elasticsearch (http://es:9200) via network 'ragnet'..."
ES_STATUS=$(docker run --rm --network ragnet curlimages/curl:7.85.0 \
  -s -o /dev/null -w "%{http_code}" http://es:9200)

if [ "$ES_STATUS" = "200" ]; then
  ES_BODY=$(docker run --rm --network ragnet curlimages/curl:7.85.0 -s http://es:9200)
  echo "✅ Elasticsearch OK (HTTP 200)"
  echo "$ES_BODY"
else
  echo "❌ Elasticsearch error (HTTP $ES_STATUS)"
fi

# 6. Cek status API
echo
echo "🔍 Mengecek API (http://localhost:8081/health)..."
API_RESULT=$(curl -s -w "\nHTTP_CODE:%{http_code}" http://localhost:8081/health)
API_STATUS=$(echo "$API_RESULT" | awk -F'HTTP_CODE:' '{print $2}')
API_BODY=$(echo "$API_RESULT" | sed -e 's/HTTP_CODE:.*//')

if [ "$API_STATUS" = "200" ]; then
  echo "✅ API OK (HTTP 200) — Response: $API_BODY"
else
  echo "❌ API error (HTTP $API_STATUS)"
fi

echo
echo "✅ Deployment complete!"
echo "   • Elasticsearch: http://localhost:9200"
echo "   • API health:   http://localhost:8081/health"
