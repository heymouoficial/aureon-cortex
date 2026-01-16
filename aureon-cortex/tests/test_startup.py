
import os
import sys
import json

# Set Mock Env Vars matching setup_vps_env.sh
os.environ["HOSTINGER_API_KEY"] = "dGtHWck8frx6DmKGoUxm53Z5bSwyv7pqfql7LOHO0a3aa5cd"
os.environ["MISTRAL_API_KEY"] = "sBi1djHcugqHtMHLJ4ROrKCG3AILMJcL"
os.environ["GEMINI_API_KEY"] = "AIzaSyD8fWY2DBPDm7f7i3cRcr70DWrpUR-GKq8"
os.environ["GEMINI_KEY_POOL"] = '["AIzaSyD8fWY2DBPDm7f7i3cRcr70DWrpUR-GKq8"]'
os.environ["SUPABASE_URL"] = "https://wkjlpfwiflecwwnrvvcv.supabase.co"
os.environ["SUPABASE_KEY"] = "mock_key" # Should be fine if not connecting immediately
os.environ["TELEGRAM_BOT_TOKEN"] = "mock_token"
os.environ["N8N_WEBHOOK_URL"] = "https://mock.url"
os.environ["N8N_API_KEY"] = "mock_key"

print("🔍 ENV VARS SET. CURRENT DIR:", os.getcwd())
print("PYTHONPATH:", sys.path)

print("🚀 Attempting to import app.main...")
try:
    from app.main import app
    print("✅ SUCCESS: app.main imported and initialized.")
except Exception as e:
    print(f"❌ FAILURE: {e}")
    import traceback
    traceback.print_exc()
