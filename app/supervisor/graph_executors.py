"""Graph executors for different subgraphs."""

from typing import Any, Dict

from langgraph.types import Command

from app.state.graph_state import SessionState
from app.utils.logger import get_logger

logger = get_logger()


class GraphExecutor:
    """Base class for graph executors."""
    
    def __init__(self, graph_name: str):
        self.graph_name = graph_name
    
    def get_thread_id(self, session_id: str) -> str:
        """Generate thread ID for this graph."""
        return f"{session_id}_{self.graph_name.replace('_graph', '')}"
    
    def get_config(self, session_id: str) -> Dict[str, Any]:
        """Get LangGraph config with thread ID."""
        return {
            "configurable": {
                "thread_id": self.get_thread_id(session_id)
            }
        }
    
    async def resume(self, message: str, session_id: str) -> Dict[str, Any]:
        """Resume an interrupted graph."""
        raise NotImplementedError
    
    async def execute(self, message: str, state: SessionState, intent_result: Dict, risk_result: Dict) -> Dict[str, Any]:
        """Execute the graph for the first time."""
        raise NotImplementedError
    
    def handle_interrupt(self, result: Dict[str, Any], state: SessionState, intent_result: Dict = None, risk_result: Dict = None) -> Dict[str, Any]:
        """Handle graph interruption (pause)."""
        interrupt_data = result["__interrupt__"][0].value
        state.waiting_for_user_input = True
        state.pending_question = interrupt_data["question"]
        
        logger.info(f"⏸️  {self.graph_name} paused: {interrupt_data['question']}")
        
        response = {
            "action": "paused",
            "graph": self.graph_name,
            "response": interrupt_data["question"],
            "metadata": self._build_pause_metadata(interrupt_data)
        }
        
        # Add classification metadata if available
        if intent_result:
            response["metadata"]["intent_confidence"] = intent_result.get("confidence")
        if risk_result:
            response["metadata"]["risk_reasoning"] = risk_result.get("reasoning")
        
        return response
    
    def handle_completion(self, result: Dict[str, Any], state: SessionState, intent_result: Dict = None, risk_result: Dict = None) -> Dict[str, Any]:
        """Handle graph completion."""
        state.waiting_for_user_input = False
        state.pending_question = None
        state.complete_graph()
        
        logger.info(f"✅ {self.graph_name} completed")
        
        response = {
            "action": "completed",
            "graph": self.graph_name,
            "response": result.get("final_response", self._get_default_completion_message()),
            "metadata": self._build_completion_metadata(result)
        }
        
        # Add classification metadata if available
        if intent_result:
            response["metadata"]["intent_confidence"] = intent_result.get("confidence")
        if risk_result:
            response["metadata"]["risk_reasoning"] = risk_result.get("reasoning")
        
        return response
    
    def _build_pause_metadata(self, interrupt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build metadata for paused state. Override in subclasses."""
        return {
            "type": interrupt_data.get("type"),
            "iteration": interrupt_data.get("iteration", 0)
        }
    
    def _build_completion_metadata(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Build metadata for completed state. Override in subclasses."""
        return {
            "next_action": result.get("next_action")
        }
    
    def _get_default_completion_message(self) -> str:
        """Get default completion message. Override in subclasses."""
        return f"Thank you for using {self.graph_name}."


class SymptomsGraphExecutor(GraphExecutor):
    """Executor for symptoms graph."""
    
    def __init__(self):
        super().__init__("symptoms_graph")
    
    async def resume(self, message: str, session_id: str) -> Dict[str, Any]:
        """Resume symptoms graph with user's answer."""
        from app.graphs.symptoms_graph.graph import symptoms_graph
        
        config = self.get_config(session_id)
        result = await symptoms_graph.ainvoke(Command(resume=message), config=config)
        
        return result
    
    async def _handle_result(self, result: Dict[str, Any], state: SessionState, 
                            intent_result: Dict = None, risk_result: Dict = None) -> Dict[str, Any]:
        """Handle graph result - check for handoff or completion.
        
        This method is called from both execute() and after processing resume results.
        """
        # Check if we need to handoff to doctor_matching_graph
        next_action = result.get("next_action")
        if next_action == "handoff_doctor":
            logger.info("[SymptomsGraphExecutor] Handoff to doctor_matching_graph requested")
            
            # Prepare handoff data
            state.handoff_data = {
                "source": "symptoms_graph",
                "symptoms_summary": self._build_symptoms_summary(result),
                "structured_symptoms": result.get("structured_symptoms", []),
                "suggested_specialties": self._extract_specialties(result),
                "urgency_level": self._determine_urgency(result)
            }
            
            # Update session state
            state.suggested_specialties = state.handoff_data["suggested_specialties"]
            state.reported_symptoms = [
                symp.get("name", "") for symp in result.get("structured_symptoms", [])
            ]
            
            # Complete current graph
            state.complete_graph()
            
            # Start doctor matching graph
            state.start_graph("doctor_matching_graph")
            
            # Execute doctor matching graph
            from app.supervisor.graph_executors import get_graph_executor
            doctor_executor = get_graph_executor("doctor_matching_graph")
            
            return await doctor_executor.execute(
                message="", 
                state=state, 
                intent_result=intent_result, 
                risk_result=risk_result
            )
        
        # No handoff, just complete normally
        return self.handle_completion(result, state, intent_result, risk_result)
    
    async def execute(self, message: str, state: SessionState, intent_result: Dict, risk_result: Dict) -> Dict[str, Any]:
        """Execute symptoms graph."""
        from app.graphs.symptoms_graph.graph import symptoms_graph
        
        input_state = {
            "user_message": message,
            "session_id": state.session_id,
            "raw_symptoms": message,
            "structured_symptoms": [],
            "questions_asked": [],
            "answers_collected": {},
            "needs_more_info": False,
            "missing_info": [],
            "iteration_count": 0,
            "max_iterations": 3,
            "final_response": None,
            "next_action": "complete"
        }
        
        config = self.get_config(state.session_id)
        logger.info(f"📍 Executing {self.graph_name}")
        
        result = await symptoms_graph.ainvoke(input_state, config=config)
        
        if "__interrupt__" in result:
            return self.handle_interrupt(result, state, intent_result, risk_result)
        else:
            # Use _handle_result to check for handoff or complete
            return await self._handle_result(result, state, intent_result, risk_result)
    
    def _build_symptoms_summary(self, result: Dict[str, Any]) -> str:
        """Build a summary of symptoms for handoff."""
        symptoms = result.get("structured_symptoms", [])
        if not symptoms:
            return result.get("raw_symptoms", "")
        
        summary_parts = []
        for symp in symptoms:
            parts = [symp.get("name", "")]
            if symp.get("severity"):
                parts.append(f"({symp['severity']})")
            if symp.get("duration"):
                parts.append(f"for {symp['duration']}")
            summary_parts.append(" ".join(parts))
        
        return ", ".join(summary_parts)
    
    def _extract_specialties(self, result: Dict[str, Any]) -> List[str]:
        """Extract or infer specialties from symptoms."""
        # Simple mapping - in production, use LLM
        symptoms = result.get("structured_symptoms", [])
        specialties = set()
        
        for symp in symptoms:
            name = symp.get("name", "").lower()
            if any(word in name for word in ["skin", "rash", "acne"]):
                specialties.add("Dermatology")
            elif any(word in name for word in ["heart", "chest", "pressure"]):
                specialties.add("Cardiology")
            elif any(word in name for word in ["stomach", "digestion", "nausea"]):
                specialties.add("Gastroenterology")
            elif any(word in name for word in ["headache", "migraine", "nerve"]):
                specialties.add("Neurology")
            elif any(word in name for word in ["joint", "bone", "fracture"]):
                specialties.add("Orthopedics")
        
        return list(specialties) if specialties else ["General Medicine"]
    
    def _determine_urgency(self, result: Dict[str, Any]) -> str:
        """Determine urgency level from symptoms."""
        symptoms = result.get("structured_symptoms", [])
        
        for symp in symptoms:
            if symp.get("severity") == "severe":
                return "high"
            elif symp.get("severity") == "moderate":
                return "medium"
        
        return "low"
    
    def _build_pause_metadata(self, interrupt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build symptoms-specific pause metadata."""
        return {
            "type": interrupt_data.get("type"),
            "missing_info": interrupt_data.get("missing_info", []),
            "iteration": interrupt_data.get("iteration", 0),
            "symptoms_summary": interrupt_data.get("symptoms_summary"),
            "structured_symptoms": interrupt_data.get("structured_symptoms")
        }
    
    def _build_completion_metadata(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Build symptoms-specific completion metadata."""
        return {
            "next_action": result.get("next_action"),
            "structured_symptoms": result.get("structured_symptoms", [])
        }
    
    def _get_default_completion_message(self) -> str:
        return "Thank you for sharing your symptoms."


class DoshaGraphExecutor(GraphExecutor):
    """Executor for dosha graph."""
    
    def __init__(self):
        super().__init__("dosha_graph")
    
    async def resume(self, message: str, session_id: str) -> Dict[str, Any]:
        """Resume dosha graph with user's answer."""
        from app.graphs.dosha_graph.graph import dosha_graph
        
        config = self.get_config(session_id)
        result = await dosha_graph.ainvoke(Command(resume=message), config=config)
        
        return result
    
    async def execute(self, message: str, state: SessionState, intent_result: Dict, risk_result: Dict) -> Dict[str, Any]:
        """Execute dosha graph."""
        from app.graphs.dosha_graph.graph import dosha_graph
        
        input_state = {
            "user_message": message,
            "session_id": state.session_id,
            "answers_collected": {},
            "confidence_score": 0.0,
            "confidence_threshold": 0.7,
            "questions_asked": [],
            "needs_more_info": True,
            "missing_areas": [],
            "iteration_count": 0,
            "max_iterations": 5,
            "vata_score": None,
            "pitta_score": None,
            "kapha_score": None,
            "dominant_dosha": None,
            "dosha_explanation": None,
            "final_response": None,
            "safety_flags": [],
            "next_action": "complete"
        }
        
        config = self.get_config(state.session_id)
        logger.info(f"📍 Executing {self.graph_name}")
        
        result = await dosha_graph.ainvoke(input_state, config=config)
        
        if "__interrupt__" in result:
            return self.handle_interrupt(result, state, intent_result, risk_result)
        else:
            return self.handle_completion(result, state, intent_result, risk_result)
    
    def _build_pause_metadata(self, interrupt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build dosha-specific pause metadata."""
        return {
            "type": interrupt_data.get("type"),
            "missing_areas": interrupt_data.get("missing_areas", []),
            "confidence": interrupt_data.get("confidence", 0.0),
            "iteration": interrupt_data.get("iteration", 0)
        }
    
    def _build_completion_metadata(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Build dosha-specific completion metadata."""
        return {
            "next_action": result.get("next_action"),
            "vata_score": result.get("vata_score"),
            "pitta_score": result.get("pitta_score"),
            "kapha_score": result.get("kapha_score"),
            "dominant_dosha": result.get("dominant_dosha"),
            "safety_flags": result.get("safety_flags", [])
        }
    
    def _get_default_completion_message(self) -> str:
        return "Thank you for completing the dosha assessment."

class EmergencyGraphExecutor(GraphExecutor):
    """Executor for emergency graph."""

    def __init__(self):
        super().__init__("emergency_graph")

    async def resume(self, message: str, session_id: str) -> Dict[str, Any]:
        """Resume emergency graph (no interrupts expected, but support resume)."""
        from app.graphs.emergency_graph.graph import emergency_graph
        config = self.get_config(session_id)
        # Emergency graph doesn't pause; forwarding resume as a fresh invoke
        result = await emergency_graph.ainvoke(Command(resume=message), config=config)
        return result

    async def execute(self, message: str, state: SessionState, intent_result: Dict, risk_result: Dict) -> Dict[str, Any]:
        """Execute emergency graph with initial state."""
        from app.graphs.emergency_graph.graph import emergency_graph

        input_state = {
            "user_message": message,
            "session_id": state.session_id,
            "incident_summary": None,
            "emergency_type": None,
            "risk_level": None,
            "detected_keywords": [],
            "needs_911": False,
            "urgency_score": 0.0,
            "first_aid_instructions": None,
            "escalation_advice": None,
            "final_response": None,
            "safety_flags": [],
            "next_action": "complete",
            "completed": False,
        }

        config = self.get_config(state.session_id)
        logger.info(f"📍 Executing {self.graph_name}")

        result = await emergency_graph.ainvoke(input_state, config=config)

        # Emergency graph is linear; handle as completion
        return self.handle_completion(result, state, intent_result, risk_result)

    def _get_default_completion_message(self) -> str:
        return "Emergency guidance provided. Please seek immediate medical attention."


class DoctorMatchingGraphExecutor(GraphExecutor):
    """Executor for doctor matching graph."""
    
    def __init__(self):
        super().__init__("doctor_matching_graph")
    
    async def resume(self, message: str, session_id: str) -> Dict[str, Any]:
        """Resume doctor matching graph with user's answer."""
        from app.graphs.doctor_matching_graph.graph import doctor_matching_graph
        
        config = self.get_config(session_id)
        result = await doctor_matching_graph.ainvoke(Command(resume=message), config=config)
        
        return result
    
    async def execute(self, message: str, state: SessionState, intent_result: Dict, risk_result: Dict) -> Dict[str, Any]:
        """Execute simplified doctor matching graph."""
        from app.graphs.doctor_matching_graph.graph import doctor_matching_graph
        
        # Check for handoff data from previous graph (may be empty if called directly)
        handoff_data = state.handoff_data if state.handoff_data else {}
        
        # Build session context for symptoms triage - ALWAYS pass this
        # This allows the graph to check conversation history even without handoff
        recent_messages = state.get_recent_messages(n=15)  # Increased to 15 for better context
        session_context = {
            "reported_symptoms": state.reported_symptoms,
            "recent_messages": [
                {"role": msg.role, "content": msg.content}
                for msg in recent_messages
            ],
            "user_location_city": state.user_location_city,
            "suggested_specialties": state.suggested_specialties
        }
        
        logger.info(f"[DoctorMatchingExecutor] Handoff data: {bool(handoff_data)}, Reported symptoms: {state.reported_symptoms}, Recent messages: {len(recent_messages)}")
        
        # Simplified input state matching the new TypedDict
        input_state = {
            "user_message": message,
            
            # Input from handoff (may be empty if direct call)
            "symptoms_summary": handoff_data.get("symptoms_summary", ""),
            "structured_symptoms": handoff_data.get("structured_symptoms", []),
            "severity_level": handoff_data.get("urgency_level", ""),
            "handoff_source": handoff_data.get("source", ""),
            
            # Session context from global state - CRITICAL for conversation memory
            "session_context": session_context,
            
            # Will be collected during flow
            "confirmed_specialties": [],
            "user_location_city": "",
            
            # Will be populated by graph
            "available_doctors": [],
            "final_response": "",
            "next_action": "complete",
            "booking_context": {}
        }
        
        config = self.get_config(state.session_id)
        logger.info(f"📍 Executing simplified {self.graph_name}")
        
        result = await doctor_matching_graph.ainvoke(input_state, config=config)
        
        if "__interrupt__" in result:
            return self.handle_interrupt(result, state, intent_result, risk_result)
        else:
            # Store available doctors in session state for UI
            if result.get("available_doctors"):
                state.available_doctors = result["available_doctors"]
            if result.get("booking_context"):
                state.booking_context = result["booking_context"]
            
            return self.handle_completion(result, state, intent_result, risk_result)
    
    def _build_pause_metadata(self, interrupt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build doctor matching specific pause metadata."""
        return {
            "type": interrupt_data.get("type"),
            "doctors": interrupt_data.get("doctors"),
            "available_slots": interrupt_data.get("available_slots"),
            "booking_details": interrupt_data.get("booking_details")
        }
    
    def _build_completion_metadata(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Build doctor matching specific completion metadata."""
        return {
            "next_action": result.get("next_action"),
            "appointment_id": result.get("appointment_id"),
            "selected_doctor": result.get("selected_doctor", {}).get("name"),
            "appointment_date": result.get("preferred_date"),
            "appointment_time": result.get("selected_time_slot")
        }
    
    def _get_default_completion_message(self) -> str:
        return "Thank you for using our doctor booking service."


# Registry of all graph executors
GRAPH_EXECUTORS = {
    "symptoms_graph": SymptomsGraphExecutor(),
    "dosha_graph": DoshaGraphExecutor(),
    "doctor_matching_graph": DoctorMatchingGraphExecutor(),
    "emergency_graph": EmergencyGraphExecutor(),
}


def get_graph_executor(graph_name: str) -> GraphExecutor:
    """Get the appropriate graph executor."""
    executor = GRAPH_EXECUTORS.get(graph_name)
    if not executor:
        raise ValueError(f"No executor found for graph: {graph_name}")
    return executor