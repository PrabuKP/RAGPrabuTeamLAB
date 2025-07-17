# 1. Base image dengan Python 3.10
FROM python:3.10-slim

# 2. Set working directory
WORKDIR /app

# 3. Install system dependencies (untuk modul parser)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      libxml2-dev \
      libxslt1-dev \
      libzip-dev && \
    rm -rf /var/lib/apt/lists/*

# 4. Copy daftar requirements & install via pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy seluruh source code (nanti Anda tambahkan server.py, modul, dsb.)
COPY . .

# 6. (Expose port nanti di tahap berikutnya, misal 8087)
#    tapi di tahap persiapan kita tulis sebagai placeholder:
EXPOSE 8081

# 7. Default command untuk menjalankan FastAPI
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8081"]
