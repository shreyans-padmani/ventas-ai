# Optimized Dockerfile for Railway - faster builds
FROM python:3.11-slim as builder

# Install only essential build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

# Upgrade pip and tools
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements
COPY requirements.txt .

# Strategy: Install in layers for better caching
# 1. Install base dependencies first (fast)
RUN pip install --no-cache-dir --user \
    requests==2.32.3 \
    python-dotenv \
    fastapi \
    uvicorn

# 2. Install database driver
RUN pip install --no-cache-dir --user psycopg[binary]

# 3. Install Google API client
RUN pip install --no-cache-dir --user google-generativeai

# 4. Install pandas (can be slow)
RUN pip install --no-cache-dir --user pandas==2.2.3

# 5. Install PyTorch CPU-only (smaller, faster)
RUN pip install --no-cache-dir --user \
    torch==2.1.0 \
    --index-url https://download.pytorch.org/whl/cpu || \
    pip install --no-cache-dir --user torch==2.1.0

# 6. Install sentence-transformers last (uses installed torch)
RUN pip install --no-cache-dir --user sentence-transformers==2.2.2

# Final runtime stage
FROM python:3.11-slim

# Only runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy Python packages
COPY --from=builder /root/.local /root/.local

ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Copy only necessary files
COPY main.py text_to_sql.py sql_executor.py llm_interpreter.py llm_client.py database.py embeddings.py config.py prompt_builder.py ./
COPY schema.txt ./

EXPOSE 5000

CMD ["python", "main.py"]
