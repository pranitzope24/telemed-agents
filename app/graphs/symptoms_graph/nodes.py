"""Symptoms graph nodes implementation."""

from typing import Dict, Any
from langgraph.types import Command, interrupt
from app.graphs.symptoms_graph.state import SymptomsGraphState
from app.agents.symptom_triage_agent import SymptomTriageAgent
from app.agents.followup_agent import FollowupAgent
from app.graphs.symptoms_graph.prompts import RESPONSE_GENERATOR_PROMPT
from app.config.llm import LLMConfig
from app.constants.openai_constants import OpenaiModels
from app.utils.logger import get_logger

logger = get_logger()


async def symptom_triage_node(state: SymptomsGraphState) -> dict:
    """Extract and analyze symptoms from user message.
    
    Returns updates to state (not full state).
    """
    logger.info(f"[symptom_triage_node] Processing message: {state['user_message'][:100]}...")
    
    agent = SymptomTriageAgent()
    
    # Analyze symptoms
    result = await agent.analyze(
        message=state["user_message"],
        context=state.get("answers_collected", {})
    )
    
    logger.info(f"[symptom_triage_node] Extracted {len(result['symptoms'])} symptoms, needs_more_info={result['needs_more_info']}")
    
    # Return only the fields we want to update
    return {
        "structured_symptoms": result["symptoms"],
        "needs_more_info": result["needs_more_info"],
        "missing_info": result["missing_info"],
        "raw_symptoms": state["user_message"]
    }


async def followup_node(state: SymptomsGraphState) -> Command:
    """Generate follow-up question and wait for user answer.
    
    Uses interrupt() to pause execution and wait for user input.
    Returns Command to route to next node.
    """
    logger.info(f"[followup_node] Iteration {state['iteration_count']}/{state['max_iterations']}")
    
    # Check if max iterations reached
    if state["iteration_count"] >= state["max_iterations"]:
        logger.warning("[followup_node] Max iterations reached, moving to response")
        return Command(goto="response_generator")
    
    # Check if we still need more info
    if not state.get("needs_more_info", False):
        logger.info("[followup_node] No more info needed, moving to response")
        return Command(goto="response_generator")
    
    agent = FollowupAgent()
    
    # Generate follow-up question
    question = await agent.generate_question(
        symptoms=state.get("structured_symptoms", []),
        missing_info=state.get("missing_info", []),
        already_asked=state.get("questions_asked", [])
    )
    
    logger.info(f"[followup_node] Generated question: {question}")
    
    # PAUSE execution and wait for user answer
    # The interrupt() call saves state and returns question to caller
    # Execution resumes when user provides answer via Command(resume=answer)
    user_answer = interrupt({
        "type": "follow_up_question",
        "question": question,
        "missing_info": state.get("missing_info", []),
        "iteration": state["iteration_count"]
    })
    
    # When resumed, user_answer contains their response
    logger.info(f"[followup_node] Received answer: {user_answer[:100] if isinstance(user_answer, str) else user_answer}...")
    
    # Update state and route back to triage for re-analysis
    updated_answers = state.get("answers_collected", {}).copy()
    updated_answers[question] = str(user_answer)
    
    return Command(
        goto="symptom_triage",
        update={
            "user_message": str(user_answer),  # Re-analyze with new answer
            "questions_asked": [question],  # Appends due to Annotated[List, add]
            "answers_collected": updated_answers,
            "iteration_count": state["iteration_count"] + 1
        }
    )


async def response_generator_node(state: SymptomsGraphState) -> Dict[str, Any]:
    """Generate final response based on collected symptom information."""
    logger.info("[response_generator_node] Generating final response")
    
    llm_config = LLMConfig(model_name=OpenaiModels.GPT_4O_MINI.value, temperature=0.7)
    llm = llm_config.get_llm_instance()
    
    # Format symptoms summary
    symptoms_summary = ""
    if state.get("structured_symptoms"):
        for symptom in state["structured_symptoms"]:
            parts = [symptom.get("name", "Unknown")]
            if symptom.get("severity"):
                parts.append(f"(Severity: {symptom['severity']})")
            if symptom.get("duration"):
                parts.append(f"(Duration: {symptom['duration']})")
            if symptom.get("location"):
                parts.append(f"(Location: {symptom['location']})")
            symptoms_summary += "- " + " ".join(parts) + "\\n"
    else:
        symptoms_summary = f"- {state.get('raw_symptoms', 'Reported symptoms')}\\n"
    
    # Format additional context
    additional_context = ""
    if state.get("answers_collected"):
        additional_context = "Follow-up information provided:\\n"
        for q, a in state["answers_collected"].items():
            additional_context += f"Q: {q}\\nA: {a}\\n\\n"
    
    # Generate response
    prompt = RESPONSE_GENERATOR_PROMPT.format(
        symptoms_summary=symptoms_summary.strip(),
        additional_context=additional_context.strip() or "(No additional context)"
    )
    
    try:
        response = await llm.ainvoke(prompt)
        final_response = response.content.strip()
    except Exception as e:
        logger.error(f"[response_generator_node] Error generating LLM response: {e}")
        final_response = "I apologize, but I'm having trouble generating a response. Please consult with a healthcare provider about your symptoms."
        return {
            "final_response": final_response,
            "next_action": "complete"
        }
    
    # Check if symptoms warrant doctor consultation (outside try-except)
    symptoms = state.get("structured_symptoms", [])
    needs_doctor = any(
        symp.get("severity") in ["moderate", "severe"] 
        for symp in symptoms
    )
    
    # If moderate/severe symptoms, offer doctor booking
    if needs_doctor:
        logger.info("[response_generator_node] Symptoms warrant doctor consultation")
        
        # Add handoff offer to response
        handoff_question = "\\n\\n**Would you like me to help you find and book a doctor for consultation?**"
        
        # Interrupt to ask user (NOT in try-except)
        user_answer = interrupt({
            "type": "doctor_handoff_offer",
            "question": final_response + handoff_question,
            "symptoms_summary": symptoms_summary.strip(),
            "structured_symptoms": symptoms
        })
        
        answer_lower = str(user_answer).lower()
        
        # Check if user wants to book doctor
        if any(word in answer_lower for word in ["yes", "book", "find", "doctor", "ok", "sure"]):
            logger.info("[response_generator_node] User wants doctor booking, setting handoff")
            return {
                "final_response": final_response,
                "next_action": "handoff_doctor",
                "structured_symptoms": symptoms  # Pass symptoms for handoff
            }
    
    logger.info(f"[response_generator_node] Generated response ({len(final_response)} chars)")
    
    return {
        "final_response": final_response,
        "next_action": "complete"
    }
