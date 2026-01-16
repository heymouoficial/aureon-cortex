"""
Aureon Agentes - Multi-Agent System
🧠 Aureon Cortex: Polímata Enrutador
"""
from app.agentes.router import aureon_cortex, AureonCortex
from app.agentes.lumina import Lumina
from app.agentes.nux import Nux
from app.agentes.memoris import Memoris
from app.agentes.vox import Vox

__all__ = [
    "aureon_cortex",
    "AureonCortex",
    "Lumina",   # ✨ Estrategia
    "Nux",      # ⚡ Ventas
    "Memoris",  # 📚 RAG
    "Vox"       # 🎙️ Comunicación
]
