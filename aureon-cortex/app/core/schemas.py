from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class MemoryDomain(str, Enum):
    INTENTION = "intention"    # The "Why" - User's core goal
    PLAN = "plan"             # The "How" - Logical steps
    FACT = "fact"             # The "What" - Hard data/knowledge
    VIBE = "vibe"             # The "Feeling" - Contextual/Emotional nuance
    ACTION = "action"         # The "Done" - Execution results

class StrategicPlanStep(BaseModel):
    step_number: int
    description: str
    tool_required: Optional[str] = None
    status: str = "pending"

class StrategicMemory(BaseModel):
    """Core cognitive container for Aureon's thinking process."""
    domain: MemoryDomain
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    tags: List[str] = Field(default_factory=list)
    confidence_score: float = 1.0

class UserIntention(BaseModel):
    raw_query: str
    detected_intent: str
    entities: List[str]
    vibe_check: str  # Emotional context or project health
    urgency: int = 1 # 1 to 5

class ThinkingPlan(BaseModel):
    """The structured plan before execution (Plan-then-Execute)."""
    goal: str
    steps: List[StrategicPlanStep]
    risks_detected: List[str]
    hybrid_routing: str = "gemini-2.0-flash" # Default expert

class VibeReport(BaseModel):
    """Engineering the 'Perceived' health of a project or interaction."""
    sentiment: str
    friction_points: List[str]
    suggested_warmth_level: int # 1 (Stoic) to 5 (Mentor/Warm)
    project_status_color: str   # Liquid aesthetic: 'blue', 'gold', 'clear'
