# 1. Base image dengan Python 3.10
FROM python:3.10-slim

# 2. Set working directory
WORKDIR /app

# 3. Install system deps untuk parser
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      libxml2-dev \
      libxslt1-dev \
      libzip-dev && \
    rm -rf /var/lib/apt/lists/*

# 4. Copy requirements & install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy seluruh source code
COPY . .

# 6. Expose port 8081
EXPOSE 8081

# 7. Jalankan Uvicorn di port 8081
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8081"]
