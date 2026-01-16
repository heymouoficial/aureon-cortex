# Imagen base optimizada para Aureon Cortex
FROM python:3.11-slim

# Variables de entorno críticas
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PNPM_HOME="/root/.local/share/pnpm"
ENV PATH="${PNPM_HOME}:${PATH}:/usr/local/bin"

WORKDIR /app

# 1. Instalar dependencias de sistema y Node.js
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ca-certificates \
    gnupg \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list \
    && apt-get update && apt-get install nodejs -y \
    && npm install -g pnpm \
    && mkdir -p $PNPM_HOME \
    && rm -rf /var/lib/apt/lists/*

# 2. Pre-instalar Servidores MCP (nombres correctos de npm)
RUN pnpm add -g \
    @supabase/mcp-server-supabase \
    @notionhq/notion-mcp-server \
    @modelcontextprotocol/server-sequential-thinking \
    @pinecone-database/mcp \
    @upstash/context7-mcp

# 3. Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiar el código del Cortex
COPY . .

# Exponer puerto para Dokploy
EXPOSE 8080

# Comando de inicio
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers"]
