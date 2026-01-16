# 🧠 Aureon Cortex - Dockerfile
# Optimized for VPS Deployment (Hostinger/DigitalOcean)

FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies (gcc needed for some python packages)
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- Runtime Stage ---
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Environment Defaults
ENV PYTHONPATH=/app
ENV PORT=8000
ENV MODULE_NAME="app.main"

# Expose port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run Application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
