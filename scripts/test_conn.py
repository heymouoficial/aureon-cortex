import httpx
import os

SUPABASE_URL = "https://rbpgcwmklmyaxnekxxvb.supabase.co"
SUPABASE_KEY = "sb_secret_v8yIIWMlKKx-Y3JGzz2Lxg_EpnmAB8F"

async def test():
    url = f"{SUPABASE_URL}/rest/v1/document_chunks?select=count"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, headers=headers)
            print(f"Status: {resp.status_code}")
            print(f"Body: {resp.text}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test())
