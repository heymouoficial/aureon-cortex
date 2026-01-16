# Aureon Cortex 🧠

> The Cognitive Operating System Backend for Multiversa

## 🚀 Dokploy Deployment

This service is designed to be deployed via **Dokploy** from the GitHub repository.

### Quick Deploy

1. In Dokploy, click **"+ Create Project"** → **"Aureon Cortex"**
2. Add a new **Application** → Choose **"Docker"**
3. Select **"Git"** as source → Connect to `heymouoficial/multiversa-lab`
4. Set **Build Path**: `aureon-cortex`
5. Configure the domain: `cortex.elevatmarketing.com`

### Environment Variables (Required)

Add these in Dokploy's **Environment** tab:

```env
# AI Providers
GEMINI_API_KEY=your_key
GEMINI_KEY_POOL=["key1","key2","key3","key4"]
MISTRAL_API_KEY=your_key
GROQ_API_KEY=your_key
OPENAI_API_KEY=your_key
DEEPSEEK_API_KEY=your_key

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
SUPABASE_ANON_KEY=your_anon_key

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token

# Domain (for webhook)
DOMAIN=https://cortex.elevatmarketing.com

# N8N Integration
N8N_WEBHOOK_URL=https://n8n.elevatmarketing.com/webhook/...
N8N_API_KEY=your_n8n_key
```

### Health Check

- **Endpoint**: `GET /health`
- **Expected Response**: `{"status": "ok", "service": "cortex"}`

### API Endpoints

| Endpoint                  | Method | Description        |
| ------------------------- | ------ | ------------------ |
| `/health`                 | GET    | Health check       |
| `/api/v1/synapse/process` | POST   | AI chat processing |
| `/telegram/webhook`       | POST   | Telegram updates   |
| `/docs`                   | GET    | Swagger UI         |

---

## 🛡️ Intellectual Property

Protected by **SafeCreative** - [Registration #2501166597628](https://www.safecreative.org/work/2501166597628)

**Built by Multiversa Lab** 🇻🇪
