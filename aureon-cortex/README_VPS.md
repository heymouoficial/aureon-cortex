# 🧠 Despliegue de Aureon Cortex en VPS

Aureon Cortex está diseñado para correr en contenedor, ideal para tu VPS junto a n8n.

## Requisitos Previos en VPS

- Docker & Docker Compose
- Acceso a Internet (para bajar paquetes)
- Puerto 8000 libre (o configurar Reverse Proxy)

## Pasos de Despliegue Rápido

### 1. Variables de Entorno

Crea un archivo `.env.cortex` en la raíz de `cortex/`:

```bash
SUPABASE_URL="https://tu-proyecto.supabase.co"
SUPABASE_KEY="tu-service-role-key"
GEMINI_API_KEY="tu-api-key"
```

### 2. Construir Imagen

```bash
docker build -t aureon-cortex:latest .
```

### 3. Correr Contenedor

```bash
# Ejecutar en segundo plano, reinicio automático
docker run -d \
  --name aureon-cortex \
  --restart unless-stopped \
  -p 8000:8000 \
  --env-file .env.cortex \
  aureon-cortex:latest
```

### 4. Verificar

Visita `http://TU_IP_VPS:8000/docs` para ver el Swagger UI.

## Conexión con n8n

Desde n8n (que está en el mismo VPS o red), puedes llamar al Cortex usando `http://host.docker.internal:8000` si usas red bridge, o la IP pública.
