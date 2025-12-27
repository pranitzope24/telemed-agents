"""Main session state for conversation tracking."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from app.state.base_state import BaseState


class Message(BaseModel):
    """Individual message in conversation."""
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SessionState(BaseState):
    """Main session state tracking entire conversation."""
    
    # ===== Identity =====
    session_id: str
    user_id: Optional[str] = None
    
    # ===== Conversation History =====
    messages: List[Message] = Field(default_factory=list)
    message_count: int = 0
    
    # ===== Intent & Routing =====
    current_intent: Optional[Literal[
        "symptom",
        "dosha",
        "doctor",
        "prescription",
        "progress",
        "emergency",
        "general"
    ]] = None
    intent_confidence: Optional[float] = None
    
    # ===== Graph Execution =====
    active_graph: Optional[Literal[
        "symptoms_graph",
        "dosha_graph",
        "doctor_matching_graph",
        "prescription_graph",
        "progress_graph",
        "emergency_graph"
    ]] = None
    active_node: Optional[str] = None
    graph_started_at: Optional[datetime] = None
    
    # ===== Medical Safety =====
    risk_level: Literal["low", "medium", "high", "emergency"] = "low"
    safety_flags: List[str] = Field(default_factory=list)
    emergency_keywords_detected: List[str] = Field(default_factory=list)
    requires_human_review: bool = False
    
    # ===== Medical Context (Summary) =====
    reported_symptoms: List[str] = Field(default_factory=list)
    triage_outcome: Optional[Literal["needs_doctor", "self_care", "emergency"]] = None
    suggested_specialties: List[str] = Field(default_factory=list)
    
    # ===== Flow Control =====
    status: Literal["active", "waiting", "completed", "terminated"] = "active"
    waiting_for_user_input: bool = False
    clarification_needed: bool = False
    pending_question: Optional[str] = None
    
    # ===== Graph Handoff =====
    handoff_data: Dict[str, Any] = Field(default_factory=dict)
    previous_graph: Optional[str] = None
    graph_history: List[str] = Field(default_factory=list)
    
    # ===== User Context (Optional) =====
    user_name: Optional[str] = None
    user_age: Optional[int] = None
    user_language: str = "en"
    
    # ===== Session Metadata =====
    session_notes: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None) -> "SessionState":
        """Add a message to the conversation."""
        message = Message(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(message)
        self.message_count = len(self.messages)
        self.update_timestamp()
        return self
    
    def get_recent_messages(self, n: int = 10) -> List[Message]:
        """Get the last n messages."""
        return self.messages[-n:] if self.messages else []
    
    def add_safety_flag(self, flag: str) -> "SessionState":
        """Add a safety flag."""
        if flag not in self.safety_flags:
            self.safety_flags.append(flag)
        self.update_timestamp()
        return self
    
    def start_graph(self, graph_name: str) -> "SessionState":
        """Mark the start of a graph execution."""
        if self.active_graph:
            self.previous_graph = self.active_graph
            self.graph_history.append(self.active_graph)
        
        self.active_graph = graph_name
        self.graph_started_at = datetime.now()
        self.update_timestamp()
        return self
    
    def complete_graph(self) -> "SessionState":
        """Mark graph completion and clear active state."""
        if self.active_graph:
            self.graph_history.append(self.active_graph)
            self.previous_graph = self.active_graph
        
        self.active_graph = None
        self.active_node = None
        self.graph_started_at = None
        self.update_timestamp()
        return self
    
    def is_emergency(self) -> bool:
        """Check if session is in emergency state."""
        return self.risk_level == "emergency" or self.triage_outcome == "emergency"
    
    def get_conversation_summary(self) -> str:
        """Get a brief summary of the conversation."""
        summary_parts = []
        
        if self.current_intent:
            summary_parts.append(f"Intent: {self.current_intent}")
        
        if self.reported_symptoms:
            summary_parts.append(f"Symptoms: {', '.join(self.reported_symptoms[:3])}")
        
        if self.risk_level != "low":
            summary_parts.append(f"Risk: {self.risk_level}")
        
        if self.active_graph:
            summary_parts.append(f"Graph: {self.active_graph}")
        
        return " | ".join(summary_parts) if summary_parts else "New session"
