# Google Workspace Setup para Aureon Cortex

## Prerrequisitos

Tienes el archivo `eco-diode-464621-h9-08a5c8b86b3f.json` que contiene las credenciales del Service Account.

## Configuración en Dokploy

### Opción A: Variable de Entorno (Recomendada)

1. Ve a **Dokploy** → **Application: Aureon Cortex V2** → **Environment**

2. Agrega la siguiente variable:

```
GOOGLE_APPLICATION_CREDENTIALS_JSON=<contenido del JSON en una sola línea>
```

**Para convertir el JSON a una línea:**

```bash
cat eco-diode-464621-h9-08a5c8b86b3f.json | jq -c .
```

3. **Redespliega** la aplicación

### Opción B: Archivo en el Container (Alternativa)

1. Copia el archivo JSON al repositorio en:

   ```
   aureon-cortex/secrets/google-creds.json  # ⚠️ Agregar a .gitignore!
   ```

2. Actualizar el código para leer desde esa ruta

---

## Permisos del Service Account

El Service Account `aureon-cortex@eco-diode-464621-h9.iam.gserviceaccount.com` necesita:

### APIs a Habilitar (Google Cloud Console)

1. **Google Calendar API**
2. **Gmail API**
3. **Google Drive API**

### Para acceder a calendarios/correos de usuarios:

1. Ve a [Google Admin Console](https://admin.google.com) (necesitas ser admin del workspace)
2. **Security** → **API Controls** → **Domain-wide Delegation**
3. Agrega el `client_id`: `104716698582589393137`
4. Scopes necesarios:

```
https://www.googleapis.com/auth/calendar
https://www.googleapis.com/auth/gmail.readonly
https://www.googleapis.com/auth/drive.readonly
```

---

## Variables de Entorno Requeridas en Dokploy

Para el MCP Server de Google Workspace:

```env
GOOGLE_CLIENT_ID=104716698582589393137
GOOGLE_CLIENT_SECRET=<no aplica para service accounts>
GOOGLE_REFRESH_TOKEN=<no aplica para service accounts>
```

**Nota:** Para Service Accounts, la autenticación es diferente. El MCP server `@modelcontextprotocol/server-google-workspace` puede requerir OAuth2 en lugar de Service Account. Verifica la documentación del MCP server.

---

## Verificación

Cuando Aureon arranque, ya no deberías ver:

```
WARNING: Google credentials not found at /app/aureon-google-creds.json
```

En su lugar verás:

```
INFO: Google Workspace initialized successfully
```
