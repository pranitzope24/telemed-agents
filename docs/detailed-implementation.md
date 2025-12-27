# Detailed Implementation Guide

This document provides granular implementation steps for each component of the Agentic AI Chatbot system, organized by phase.

---

## Phase 1: Foundation Setup

### 1.1 Environment & Dependencies

**File: `requirements.txt`**
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
redis==5.0.1
psycopg2-binary==2.9.9
sqlalchemy==2.0.25
pydantic==2.5.3
pydantic-settings==2.1.0
python-dotenv==1.0.0
langchain==0.1.0
langgraph==0.0.20
langchain-openai==0.0.2
openai==1.7.2
anthropic==0.8.1
tiktoken==0.5.2
numpy==1.26.3
pandas==2.1.4
```

**File: `.env.example`**
```env
# LLM Configuration
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DEFAULT_LLM_PROVIDER=openai
DEFAULT_MODEL=gpt-4-turbo-preview

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# PostgreSQL Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/telemed_db

# Application
APP_ENV=development
LOG_LEVEL=INFO
SESSION_TTL=3600
MAX_TURNS_IN_MEMORY=10
```

### 1.2 Core Configuration Implementation

**File: `app/config/settings.py`**
```python
from pydantic_settings import BaseSettings
from typing import Literal

class Settings(BaseSettings):
    # LLM
    openai_api_key: str
    anthropic_api_key: str | None = None
    default_llm_provider: Literal["openai", "anthropic"] = "openai"
    default_model: str = "gpt-4-turbo-preview"
    
    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None
    
    # Database
    database_url: str
    
    # Application
    app_env: Literal["development", "staging", "production"] = "development"
    log_level: str = "INFO"
    session_ttl: int = 3600
    max_turns_in_memory: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

**File: `app/config/llm.py`**
```python
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from app.config.settings import settings

def get_llm(model: str | None = None, temperature: float = 0.7):
    """Get configured LLM instance."""
    model = model or settings.default_model
    
    if settings.default_llm_provider == "openai":
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            openai_api_key=settings.openai_api_key
        )
    elif settings.default_llm_provider == "anthropic":
        return ChatAnthropic(
            model=model,
            temperature=temperature,
            anthropic_api_key=settings.anthropic_api_key
        )
    else:
        raise ValueError(f"Unknown LLM provider: {settings.default_llm_provider}")
```

**File: `app/utils/logger.py`**
```python
import logging
import sys
from app.config.settings import settings

def setup_logger(name: str) -> logging.Logger:
    """Set up structured logger."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger
```

### 1.3 State Management Foundation

**File: `app/state/base_state.py`**
```python
from dataclasses import dataclass, asdict
from typing import Any, Dict
import json

@dataclass
class BaseState:
    """Base state class with serialization."""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create from dictionary."""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str):
        """Create from JSON string."""
        return cls.from_dict(json.loads(json_str))
```

**File: `app/state/graph_state.py`**
```python
from dataclasses import dataclass, field
from typing import List, Dict, Any, Literal
from app.state.base_state import BaseState

@dataclass
class Message:
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: str

@dataclass
class SessionState(BaseState):
    """Global session state shared across graphs."""
    session_id: str
    intent: str | None = None
    active_graph: str | None = None
    active_node: str | None = None
    risk_level: Literal["low", "medium", "high", "emergency"] = "low"
    safety_flags: List[str] = field(default_factory=list)
    recent_turns: List[Dict[str, Any]] = field(default_factory=list)
    handoff_data: Dict[str, Any] = field(default_factory=dict)
    profile_ref: str | None = None
```

**File: `app/memory/short_term.py`**
```python
import redis
from typing import Any
from app.config.settings import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class RedisMemory:
    """Redis-backed short-term memory."""
    
    def __init__(self):
        self.client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password,
            decode_responses=True
        )
    
    def set(self, key: str, value: str, ttl: int | None = None) -> bool:
        """Set value with optional TTL."""
        try:
            ttl = ttl or settings.session_ttl
            self.client.setex(key, ttl, value)
            return True
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False
    
    def get(self, key: str) -> str | None:
        """Get value by key."""
        try:
            return self.client.get(key)
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete key."""
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"Redis exists error: {e}")
            return False

# Singleton instance
redis_memory = RedisMemory()
```

### 1.4 Basic API Implementation

**File: `app/api/health.py`**
```python
from fastapi import APIRouter
from app.memory.short_term import redis_memory

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    redis_ok = redis_memory.client.ping()
    
    return {
        "status": "healthy" if redis_ok else "degraded",
        "redis": "connected" if redis_ok else "disconnected"
    }
```

**File: `app/api/chat.py`**
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

from app.state.graph_state import SessionState
from app.memory.short_term import redis_memory
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint."""
    # Generate or use existing session ID
    session_id = request.session_id or str(uuid.uuid4())
    state_key = f"session:{session_id}:session_state"
    
    # Load or create session state
    state_json = redis_memory.get(state_key)
    if state_json:
        state = SessionState.from_json(state_json)
    else:
        state = SessionState(session_id=session_id)
    
    # Add user message to recent turns
    state.recent_turns.append({
        "role": "user",
        "content": request.message,
        "timestamp": datetime.now().isoformat()
    })
    
    # Keep only last N turns
    from app.config.settings import settings
    state.recent_turns = state.recent_turns[-settings.max_turns_in_memory:]
    
    # Echo response for now (will be replaced by supervisor)
    response_text = f"Echo: {request.message}"
    
    state.recent_turns.append({
        "role": "assistant",
        "content": response_text,
        "timestamp": datetime.now().isoformat()
    })
    
    # Save state
    redis_memory.set(state_key, state.to_json())
    
    logger.info(f"Chat session {session_id}: {request.message[:50]}")
    
    return ChatResponse(response=response_text, session_id=session_id)
```

**File: `app/main.py`** (FastAPI entry point)
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import health, chat
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

app = FastAPI(title="Agentic AI Chatbot", version="0.1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(chat.router, tags=["Chat"])

@app.on_event("startup")
async def startup_event():
    logger.info("Application starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Test Phase 1:**
```bash
# Start Redis
docker run -d -p 6379:6379 redis:latest

# Run app
python app/main.py

# Test
curl http://localhost:8000/health
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '{"message": "hello"}'
```

---

## Phase 2: Supervisor & Routing

### 2.1 Intent Classifier

**File: `app/supervisor/intent_classifier.py`**
```python
from app.config.llm import get_llm
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

INTENT_PROMPT = """Classify the user's intent into one of these categories:
- symptom: User describing symptoms or health concerns
- dosha: User asking about Ayurvedic constitution or prakriti
- doctor: User wants to find or book a doctor
- prescription: User asking about medications or prescriptions
- progress: User tracking progress or follow-up
- emergency: Urgent medical emergency
- general: General questions or chitchat

User message: {message}

Respond with ONLY the intent category (lowercase, single word)."""

async def classify_intent(message: str, context: list = None) -> str:
    """Classify user intent using LLM."""
    try:
        llm = get_llm(temperature=0.3)
        
        # Add context if available
        prompt = INTENT_PROMPT.format(message=message)
        if context:
            last_turns = "\n".join([f"{t['role']}: {t['content']}" for t in context[-3:]])
            prompt = f"Previous conversation:\n{last_turns}\n\n{prompt}"
        
        response = await llm.ainvoke(prompt)
        intent = response.content.strip().lower()
        
        # Validate
        valid_intents = ["symptom", "dosha", "doctor", "prescription", "progress", "emergency", "general"]
        if intent not in valid_intents:
            logger.warning(f"Invalid intent '{intent}', defaulting to 'general'")
            intent = "general"
        
        logger.info(f"Classified intent: {intent}")
        return intent
        
    except Exception as e:
        logger.error(f"Intent classification error: {e}")
        return "general"
```

### 2.2 Risk Classifier

**File: `app/supervisor/risk_classifier.py`**
```python
from app.config.llm import get_llm
from app.utils.logger import setup_logger
from typing import Literal

logger = setup_logger(__name__)

EMERGENCY_KEYWORDS = [
    "chest pain", "heart attack", "stroke", "can't breathe", "bleeding heavily",
    "unconscious", "seizure", "overdose", "suicide", "severe bleeding",
    "anaphylaxis", "choking", "severe burn"
]

RISK_PROMPT = """Assess the medical risk level of this message:
- emergency: Life-threatening, needs immediate medical attention
- high: Serious concern, needs doctor soon
- medium: Should see doctor, not urgent
- low: Minor concern or informational

User message: {message}

Respond with ONLY the risk level (lowercase, single word)."""

async def classify_risk(message: str) -> Literal["low", "medium", "high", "emergency"]:
    """Classify medical risk level."""
    message_lower = message.lower()
    
    # Quick keyword check for emergencies
    for keyword in EMERGENCY_KEYWORDS:
        if keyword in message_lower:
            logger.warning(f"Emergency keyword detected: {keyword}")
            return "emergency"
    
    try:
        llm = get_llm(temperature=0.2)
        response = await llm.ainvoke(RISK_PROMPT.format(message=message))
        risk = response.content.strip().lower()
        
        # Validate
        valid_risks = ["low", "medium", "high", "emergency"]
        if risk not in valid_risks:
            logger.warning(f"Invalid risk '{risk}', defaulting to 'medium'")
            risk = "medium"
        
        logger.info(f"Classified risk: {risk}")
        return risk
        
    except Exception as e:
        logger.error(f"Risk classification error: {e}")
        return "medium"  # Fail-safe to medium
```

### 2.3 Router

**File: `app/supervisor/router.py`**
```python
from typing import Literal
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

def route_to_graph(
    intent: str,
    risk_level: Literal["low", "medium", "high", "emergency"]
) -> str:
    """Route to appropriate graph based on intent and risk."""
    
    # Emergency always takes priority
    if risk_level == "emergency":
        logger.warning(f"Emergency route triggered (intent={intent})")
        return "emergency"
    
    # Map intents to graphs
    intent_to_graph = {
        "symptom": "symptoms",
        "dosha": "dosha",
        "doctor": "doctor_matching",
        "prescription": "prescription",
        "progress": "progress",
        "emergency": "emergency",
        "general": "symptoms"  # Default fallback
    }
    
    graph = intent_to_graph.get(intent, "symptoms")
    logger.info(f"Routing to graph: {graph} (intent={intent}, risk={risk_level})")
    
    return graph
```

### 2.4 Supervisor Graph

**File: `app/supervisor/supervisor_graph.py`**
```python
from app.supervisor.intent_classifier import classify_intent
from app.supervisor.risk_classifier import classify_risk
from app.supervisor.router import route_to_graph
from app.state.graph_state import SessionState
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

async def run_supervisor(message: str, state: SessionState) -> dict:
    """Run supervisor to classify and route."""
    
    # If already in a graph and not complete, resume it
    if state.active_graph and state.active_node:
        logger.info(f"Resuming graph: {state.active_graph} at node: {state.active_node}")
        return {
            "graph": state.active_graph,
            "resume": True,
            "state": state
        }
    
    # Classify intent and risk
    intent = await classify_intent(message, state.recent_turns)
    risk = await classify_risk(message)
    
    # Update state
    state.intent = intent
    state.risk_level = risk
    
    # Route to graph
    target_graph = route_to_graph(intent, risk)
    state.active_graph = target_graph
    
    logger.info(f"Supervisor routing: intent={intent}, risk={risk}, graph={target_graph}")
    
    return {
        "graph": target_graph,
        "resume": False,
        "state": state
    }
```

**Update `app/api/chat.py`:**
```python
# Add to imports
from app.supervisor.supervisor_graph import run_supervisor

# Replace echo logic with:
    # Run supervisor
    routing = await run_supervisor(request.message, state)
    
    # For now, mock graph responses
    graph_responses = {
        "symptoms": "I understand you're experiencing symptoms. Can you describe them in detail?",
        "dosha": "Let me help you understand your Ayurvedic constitution. I'll ask you a few questions.",
        "emergency": "⚠️ This seems urgent. Please call emergency services immediately if needed.",
        "doctor_matching": "I can help you find a suitable doctor. What specialty are you looking for?",
        "prescription": "I can help with prescription information. What would you like to know?",
        "progress": "Let's track your progress. How are you feeling today?"
    }
    
    response_text = graph_responses.get(routing["graph"], "How can I help you?")
    
    # Update state
    state = routing["state"]
```

**Test Phase 2:**
```bash
# Symptom query
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" \
  -d '{"message": "I have a headache"}'

# Emergency
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" \
  -d '{"message": "I have severe chest pain"}'
```

---

## Phase 3: First Working Graph - Symptoms

### 3.1 Symptoms State

**File: `app/graphs/symptoms_graph/state.py`**
```python
from dataclasses import dataclass, field
from typing import List, Dict, Literal
from app.state.base_state import BaseState

@dataclass
class SymptomEntry:
    name: str
    duration: str | None = None
    severity: Literal["mild", "moderate", "severe"] | None = None
    location: str | None = None

@dataclass
class SymptomsState(BaseState):
    """Symptoms graph state."""
    raw_complaint: str = ""
    normalized_complaint: str = ""
    structured_symptoms: List[SymptomEntry] = field(default_factory=list)
    triage_outcome: Literal["needs_doctor", "self_care", "emergency"] | None = None
    suggested_specialties: List[str] = field(default_factory=list)
    clarification_needed: bool = False
    ayurveda_notes: str = ""
```

### 3.2 Symptom Triage Agent

**File: `app/agents/symptom_triage_agent.py`**
```python
import json
from app.config.llm import get_llm
from app.graphs.symptoms_graph.state import SymptomsState, SymptomEntry
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

TRIAGE_PROMPT = """You are a medical triage assistant. Analyze the symptoms and provide:
1. Structured symptom extraction (name, duration, severity, location)
2. Triage recommendation (needs_doctor, self_care, emergency)
3. Suggested medical specialties if doctor needed
4. Any Ayurvedic observations

User complaint: {complaint}

Respond in JSON format:
{{
  "symptoms": [
    {{"name": "...", "duration": "...", "severity": "mild|moderate|severe", "location": "..."}}
  ],
  "triage": "needs_doctor|self_care|emergency",
  "specialties": ["specialty1", "specialty2"],
  "ayurveda_notes": "...",
  "needs_clarification": true|false,
  "clarification_question": "..." (if needed)
}}"""

async def triage_symptoms(complaint: str) -> dict:
    """Triage symptoms using LLM."""
    try:
        llm = get_llm(temperature=0.5)
        response = await llm.ainvoke(TRIAGE_PROMPT.format(complaint=complaint))
        
        # Parse JSON response
        result = json.loads(response.content)
        logger.info(f"Triage result: {result['triage']}")
        
        return result
        
    except Exception as e:
        logger.error(f"Triage error: {e}")
        # Fail-safe
        return {
            "symptoms": [],
            "triage": "needs_doctor",
            "specialties": ["general_practitioner"],
            "ayurveda_notes": "",
            "needs_clarification": False
        }
```

### 3.3 Symptoms Graph Nodes

**File: `app/graphs/symptoms_graph/nodes.py`**
```python
from app.agents.symptom_triage_agent import triage_symptoms
from app.graphs.symptoms_graph.state import SymptomsState, SymptomEntry
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

async def normalize_input_node(state: SymptomsState, message: str) -> SymptomsState:
    """Normalize user input."""
    state.raw_complaint = message
    state.normalized_complaint = message.strip().lower()
    logger.info("Input normalized")
    return state

async def triage_node(state: SymptomsState) -> SymptomsState:
    """Run triage on symptoms."""
    result = await triage_symptoms(state.normalized_complaint)
    
    # Update state
    state.structured_symptoms = [
        SymptomEntry(**s) for s in result.get("symptoms", [])
    ]
    state.triage_outcome = result.get("triage", "needs_doctor")
    state.suggested_specialties = result.get("specialties", [])
    state.ayurveda_notes = result.get("ayurveda_notes", "")
    state.clarification_needed = result.get("needs_clarification", False)
    
    logger.info(f"Triage complete: {state.triage_outcome}")
    return state

def should_ask_clarification(state: SymptomsState) -> bool:
    """Check if clarification needed."""
    return state.clarification_needed

def is_emergency(state: SymptomsState) -> bool:
    """Check if emergency."""
    return state.triage_outcome == "emergency"
```

### 3.4 Symptoms Graph Orchestration

**File: `app/graphs/symptoms_graph/graph.py`**
```python
from langgraph.graph import StateGraph, END
from app.graphs.symptoms_graph.state import SymptomsState
from app.graphs.symptoms_graph.nodes import (
    normalize_input_node,
    triage_node,
    should_ask_clarification,
    is_emergency
)
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

def create_symptoms_graph():
    """Create symptoms graph."""
    workflow = StateGraph(SymptomsState)
    
    # Add nodes
    workflow.add_node("normalize", normalize_input_node)
    workflow.add_node("triage", triage_node)
    
    # Define flow
    workflow.set_entry_point("normalize")
    workflow.add_edge("normalize", "triage")
    
    # Conditional routing from triage
    workflow.add_conditional_edges(
        "triage",
        lambda state: "emergency" if is_emergency(state) 
                     else "clarify" if should_ask_clarification(state)
                     else "complete",
        {
            "emergency": END,  # Will handoff to emergency graph
            "clarify": END,    # Will pause for clarification
            "complete": END    # Done
        }
    )
    
    return workflow.compile()

async def run_symptoms_graph(message: str) -> dict:
    """Run symptoms graph."""
    graph = create_symptoms_graph()
    state = SymptomsState()
    
    # Run graph
    result = await graph.ainvoke({"message": message})
    
    logger.info(f"Symptoms graph complete: {result.triage_outcome}")
    
    # Format response
    if result.triage_outcome == "emergency":
        response = "⚠️ Your symptoms indicate a medical emergency. Please seek immediate medical attention or call emergency services."
    elif result.clarification_needed:
        response = "Can you provide more details about your symptoms? For example, how long have you had them?"
    elif result.triage_outcome == "needs_doctor":
        specialties = ", ".join(result.suggested_specialties[:2])
        response = f"Based on your symptoms, I recommend consulting a {specialties}. Would you like me to help you find a doctor?"
    else:
        response = "Your symptoms appear mild. I can suggest some self-care options or connect you with a doctor if you prefer."
    
    return {
        "response": response,
        "state": result,
        "handoff_needed": result.triage_outcome == "emergency",
        "handoff_graph": "emergency" if result.triage_outcome == "emergency" else None
    }
```

### 3.5 Integration with API

**Update `app/api/chat.py`:**
```python
# Add to imports
from app.graphs.symptoms_graph.graph import run_symptoms_graph

# Replace mock responses with:
    # Run appropriate graph
    if routing["graph"] == "symptoms":
        graph_result = await run_symptoms_graph(request.message)
        response_text = graph_result["response"]
        
        # Handle handoffs
        if graph_result.get("handoff_needed"):
            state.active_graph = graph_result["handoff_graph"]
    else:
        # Other graphs still mocked
        response_text = graph_responses.get(routing["graph"], "How can I help you?")
```

**Test Phase 3:**
```bash
# Test symptom flow
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" \
  -d '{"message": "I have a severe headache for 3 days with nausea"}'

# Check response suggests doctor specialty
```

---

## Phase 4-10: Remaining Implementation

Due to length constraints, the pattern follows similar structure:

**For each graph:**
1. Define state in `state.py`
2. Implement agent logic
3. Create nodes in `nodes.py`
4. Build graph orchestration in `graph.py`
5. Integrate with supervisor
6. Write tests

**For RAG (Phase 6):**
1. Set up vector DB
2. Implement loaders (chunking documents)
3. Implement retrievers (embedding + search)
4. Integrate into graph nodes

**For testing (Phase 8):**
1. Unit tests for each agent
2. Integration tests for each graph
3. End-to-end flow tests
4. Safety/edge case tests

**For deployment (Phase 9-10):**
1. Dockerfile + docker-compose
2. Environment configs
3. Monitoring setup
4. Deploy to server/cloud

---

## Key Implementation Principles

1. **Start simple**: Get basic version working before optimizing
2. **Test as you build**: Write tests alongside implementation
3. **Mock external deps**: Use mocks until ready to integrate
4. **Fail-safe defaults**: Always have fallback for errors
5. **Structured logging**: Log all important events
6. **Validate inputs**: Check all user inputs and LLM outputs
7. **Graceful degradation**: System should work even if Redis/DB temporarily down

---

## Next File to Implement

Start with Phase 1 in order:
1. `requirements.txt` ✅
2. `.env.example` ✅
3. `app/config/settings.py` ✅
4. `app/config/llm.py` ✅
5. `app/utils/logger.py` ✅
6. `app/state/base_state.py` ✅
7. `app/state/graph_state.py` ✅
8. `app/memory/short_term.py` ✅
9. `app/api/health.py` ✅
10. `app/api/chat.py` ✅
11. `app/main.py` ✅

Then test before moving to Phase 2.
