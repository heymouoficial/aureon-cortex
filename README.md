# 🧠 Aureon Cortex

> **The Cognitive Operating System Backend for Multiversa**
>
> 🔒 **PROPRIETARY SOFTWARE - ALL RIGHTS RESERVED**

---

## ⚠️ INTELLECTUAL PROPERTY NOTICE

```
╔══════════════════════════════════════════════════════════════════╗
║                    🔐 LOCK-IN NOTICE 🔐                          ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  This software is the exclusive intellectual property of:       ║
║                                                                  ║
║  👥 CO-FOUNDERS: RunaQuantum & HeyMou                           ║
║  🏢 COMPANY: Multiversa Lab                                     ║
║                                                                  ║
║  Protected by SafeCreative:                                     ║
║  Registration #2501166597628                                    ║
║  https://www.safecreative.org/work/2501166597628                ║
║                                                                  ║
║  UNAUTHORIZED USE, COPYING, MODIFICATION, OR DISTRIBUTION       ║
║  IS STRICTLY PROHIBITED AND WILL BE PROSECUTED.                 ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## 🚀 Version

**v1.0.0-alpha** | Multi-Agent Architecture

| Agent         | Role               | Model      |
| ------------- | ------------------ | ---------- |
| Aureon Cortex | Polímata Enrutador | -          |
| Lumina ✨     | Estrategia         | Mistral    |
| Nux ⚡        | Ventas             | Groq       |
| Memorís 📚    | RAG                | Gemini     |
| Vox 🎙️        | Comunicación       | Gemini 2.0 |

---

## 🛠️ Deployment (Dokploy)

1. **Create Project** in Dokploy → Select **Docker**
2. **Git Source**: `heymouoficial/aureon-cortex`
3. **Domain**: `cortex.elevatmarketing.com`

### Environment Variables

```env
# AI Providers
GEMINI_API_KEY=your_key
GEMINI_KEY_POOL=["key1","key2","key3","key4"]
MISTRAL_API_KEY=your_key
GROQ_API_KEY=your_key

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_key

# Telegram
TELEGRAM_BOT_TOKEN=your_token
```

---

## 📡 API Endpoints

| Endpoint                  | Method | Description   |
| ------------------------- | ------ | ------------- |
| `/health`                 | GET    | Health check  |
| `/api/v1/synapse/process` | POST   | AI processing |
| `/docs`                   | GET    | Swagger UI    |

---

## 📜 License

**Proprietary** - See LOCK-IN notice above.

© 2026 Astursadeth / Elevate Marketing / Multiversa Lab

Built with 🇻🇪 in Venezuela | Powered by Runa Quantum
