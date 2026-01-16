import os
import asyncio
import httpx
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ORG_ID = os.getenv("ELEVATE_ORG_ID", "pmvupdwzepfdvzycyaat")

print(f"--- RAG Ingestion Debug ---")
print(f"URL: {SUPABASE_URL}")
print(f"ORG_ID: {ORG_ID}")

async def get_embedding(text: str) -> List[float]:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={GEMINI_API_KEY}"
    payload = {
        "model": "models/text-embedding-004",
        "content": {"parts": [{"text": text}]}
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, timeout=30.0)
        if response.status_code != 200:
            print(f"   ❌ Embedding Error: {response.status_code} - {response.text}")
            response.raise_for_status()
        data = response.json()
        return data["embedding"]["values"]

async def insert_to_supabase(content: str, embedding: List[float], metadata: Dict[str, Any]):
    url = f"{SUPABASE_URL}/rest/v1/documents"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    payload = {
        "content": content,
        "metadata": metadata, # Embedding field removed temporarily if column doesn't exist
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers, timeout=10.0)
        if response.status_code not in [200, 201]:
            print(f"   ❌ Supabase Error: {response.status_code} - {response.text}")
            response.raise_for_status()

def chunk_text(text: str, max_size: int = 1000) -> List[str]:
    sections = text.split("## ")
    chunks = []
    for section in sections:
        if not section.strip(): continue
        content = "## " + section if not section.startswith("#") else section
        if len(content) > max_size:
            paras = content.split("\n\n")
            curr = ""
            for p in paras:
                if len(curr) + len(p) > max_size:
                    chunks.append(curr.strip())
                    curr = p + "\n\n"
                else: curr += p + "\n\n"
            if curr: chunks.append(curr.strip())
        else: chunks.append(content.strip())
    return chunks

async def ingest_file(file_path: str):
    file_name = os.path.basename(file_path)
    print(f"📄 Processing: {file_name}")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    chunks = chunk_text(content)
    print(f"   📦 Found {len(chunks)} chunks")
    for i, chunk in enumerate(chunks):
        try:
            embedding = await get_embedding(chunk)
            await insert_to_supabase(chunk, embedding, {"file_name": file_name, "index": i})
            print(f"   ✅ Chunk {i+1} inserted")
        except Exception as e:
            print(f"   ❌ Error in chunk {i+1}: {e}")

async def main():
    rag_dir = "/Users/astursadeth/multiversa-lab/portality/cortex/RAG"
    if not os.path.exists(rag_dir):
        print(f"❌ Error: RAG folder not found at {rag_dir}")
        return
    files = [f for f in os.listdir(rag_dir) if f.endswith(".md")]
    print(f"📁 Found {len(files)} files to ingest")
    for file in files:
        await ingest_file(os.path.join(rag_dir, file))
    print("\n✨ Ingestion complete!")

if __name__ == "__main__":
    asyncio.run(main())
