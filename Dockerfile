# Base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system deps untuk parser (jika perlu)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      libxml2-dev \
      libxslt1-dev \
      libzip-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy dan install dependencies Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh kode proyek
COPY . .

# Expose port FastAPI default
EXPOSE 8087

# Command untuk menjalankan server
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8087"]
