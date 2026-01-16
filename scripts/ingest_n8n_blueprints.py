import os
import json
import zipfile
import asyncio
from typing import List, Dict, Any
from app.services.vector_search import vector_search_service
from app.core.config import get_settings
from loguru import logger

settings = get_settings()

API_KEY = settings.SUPABASE_SERVICE_ROLE_KEY
URL = settings.SUPABASE_URL

async def ingest_blueprints(zip_path: str, org_id: str = "392ecec2-e769-4db2-810f-ccd5bd09d92a"):
    """
    Ingests n8n blueprints from a ZIP file into the vector database.
    Agrupa los nodos para entender la lógica del flujo.
    """
    extracted_path = "/tmp/n8n_blueprints"
    os.makedirs(extracted_path, exist_ok=True)
    
    logger.info(f"📂 Descomprimiendo {zip_path}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extracted_path)
        
    blueprints = []
    
    # Recorrer archivos
    for root, dirs, files in os.walk(extracted_path):
        for file in files:
            if file.endswith(".json"):
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, 'r') as f:
                        data = json.load(f)
                        
                    # Validar si es un workflow de n8n
                    nodes = data.get('nodes', [])
                    connections = data.get('connections', {})
                    
                    if not nodes:
                        continue
                        
                    # Crear resumen del flujo
                    node_types = [n.get('type', 'unknown').replace('n8n-nodes-base.', '') for n in nodes]
                    node_names = [n.get('name', 'unknown') for n in nodes]
                    
                    summary = f"Workflow n8n: {file}\n"
                    summary += f"Nodos: {', '.join(set(node_types))}\n"
                    summary += f"Estructura: {len(nodes)} nodos, {len(connections)} conexiones.\n"
                    
                    # Store logic (Raw JSON is too tokens expensive, store structural summary + key logic)
                    content_to_embed = f"BLUEPRINT: {file}\nTYPE: n8n_workflow\n\nLOGIC:\n{summary}\n\nNODES:\n"
                    for n in nodes[:20]: # Limit processing
                         content_to_embed += f"- {n.get('name')} ({n.get('type')})\n"
                    
                    blueprints.append({
                        "content": content_to_embed,
                        "metadata": {
                            "file_name": file,
                            "type": "n8n_blueprint",
                            "node_count": len(nodes),
                            "raw_json_snippet": json.dumps(data)[:500] # Guardar snippet para referencia
                        }
                    })
                    
                except Exception as e:
                    logger.error(f"❌ Error leyendo {file}: {e}")

    logger.info(f"🧠 Encontrados {len(blueprints)} blueprints válidos. Inserción vectorial iniciada...")
    
    # Insertar en lotes
    count = 0
    for bp in blueprints:
        try:
            # Usar el nuevo método store_document
            success = await vector_search_service.store_document(
                content=bp["content"], 
                metadata=bp["metadata"], 
                organization_id=org_id
            )
            
            if success:
                count += 1
                logger.info(f"✅ Ingerido: {bp['metadata']['file_name']}")
            else:
                logger.warning(f"⚠️ Falló inserción: {bp['metadata']['file_name']}")
            
        except Exception as e:
            logger.error(f"❌ Error indexing {bp['metadata']['file_name']}: {e}")

    return f"Procesados e ingeridos {count} de {len(blueprints)} archivos."

if __name__ == "__main__":
    # Test local
    pass
