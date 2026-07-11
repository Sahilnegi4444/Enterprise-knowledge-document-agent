# ==========================================
# STAGE 1: Builder
# ==========================================
FROM python:3.11-slim AS builder

WORKDIR /build

# Install compilation tools needed for packages like hnswlib/chromadb
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies into a target folder
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# Pre-download the Hugging Face embedding model to bake it into the image
# This ensures offline execution and sub-second container startup
RUN PYTHONPATH=/install/lib/python3.11/site-packages python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# ==========================================
# STAGE 2: Runner
# ==========================================
FROM python:3.11-slim AS runner

WORKDIR /workspace

# Install minimal runtime system libraries (libgomp1 is required for hnswlib/chromadb OpenMP)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Create a secure, non-privileged system user/group
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -m -s /sbin/nologin appuser

# Set runtime optimization and Hugging Face offline environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HF_HOME=/home/appuser/.cache/huggingface \
    HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1

# Copy python dependencies from builder stage
COPY --from=builder /install /usr/local

# Copy pre-downloaded Hugging Face cache and set correct permissions
COPY --from=builder --chown=appuser:appgroup /root/.cache/huggingface /home/appuser/.cache/huggingface

# Copy application source code
COPY --chown=appuser:appgroup . .

# Expose FastAPI default port
EXPOSE 8000

# Switch to the secure non-root user
USER appuser

# Run the FastAPI server
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
