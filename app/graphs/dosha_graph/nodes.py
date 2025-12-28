"""Dosha graph nodes implementation."""

from typing import Dict, Any
from langgraph.types import Command, interrupt
from app.graphs.dosha_graph.state import DoshaGraphState
from app.agents.questionnaire_agent import DoshaQuestionnaireAgent
from app.agents.followup_agent import FollowupAgent
from app.agents.dosha_inference_agent import DoshaInferenceAgent
from app.safety.compliance_checker import SafetyComplianceChecker
from app.graphs.dosha_graph.prompts import (
    FOLLOWUP_QUESTION_GENERATOR_PROMPT,
    RESPONSE_GENERATOR_PROMPT
)
from app.config.llm import LLMConfig
from app.constants.openai_constants import OpenaiModels
from app.utils.logger import get_logger

logger = get_logger()


async def questionnaire_node(state: DoshaGraphState) -> dict:
    """Analyze user responses and calculate confidence score.
    
    Returns updates to state (not full state).
    """
    logger.info(f"[questionnaire_node] Processing message: {state['user_message'][:100]}...")
    
    agent = DoshaQuestionnaireAgent()
    
    # Analyze responses
    result = await agent.analyze(
        message=state["user_message"],
        context=state.get("answers_collected", {})
    )
    
    logger.info(
        f"[questionnaire_node] Confidence: {result['confidence_score']:.2f}, "
        f"needs_more_info={result['needs_more_info']}, "
        f"missing={result['missing_areas']}"
    )
    
    # Return only the fields we want to update
    return {
        "answers_collected": result["answers"],
        "confidence_score": result["confidence_score"],
        "needs_more_info": result["needs_more_info"],
        "missing_areas": result["missing_areas"]
    }


async def followup_node(state: DoshaGraphState) -> Command:
    """Generate follow-up question and wait for user answer.
    
    Uses interrupt() to pause execution and wait for user input.
    Returns Command to route to next node.
    """
    logger.info(f"[followup_node] Iteration {state['iteration_count']}/{state['max_iterations']}")
    
    # Check if max iterations reached
    if state["iteration_count"] >= state["max_iterations"]:
        logger.warning("[followup_node] Max iterations reached, moving to inference")
        return Command(goto="dosha_inference")
    
    # Check if we have enough confidence
    threshold = state.get("confidence_threshold", 0.7)
    if state.get("confidence_score", 0.0) >= threshold:
        logger.info(f"[followup_node] Confidence {state['confidence_score']:.2f} >= {threshold}, moving to inference")
        return Command(goto="dosha_inference")
    
    # Generate follow-up question
    agent = FollowupAgent()
    
    missing_areas_text = ", ".join(state.get("missing_areas", []))
    already_asked_text = "\n".join([f"- {q}" for q in state.get("questions_asked", [])])
    
    # Use custom prompt for dosha-specific questions
    llm_config = LLMConfig(model_name=OpenaiModels.GPT_4O_MINI.value, temperature=0.7)
    llm = llm_config.get_llm_instance()
    
    prompt = FOLLOWUP_QUESTION_GENERATOR_PROMPT.format(
        missing_areas=missing_areas_text or "(None)",
        already_asked=already_asked_text or "(None)"
    )
    
    try:
        response = await llm.ainvoke(prompt)
        question = response.content.strip()
        
        # Clean up
        if question.startswith('"'):
            question = question.strip('"')
        if question.startswith('Question:'):
            question = question.replace('Question:', '').strip()
            
    except Exception as e:
        logger.error(f"[followup_node] Error generating question: {e}")
        # Fallback based on missing areas
        missing = state.get("missing_areas", [])
        if missing:
            question = f"Can you tell me more about your {missing[0].replace('_', ' ')}?"
        else:
            question = "Can you provide any additional details about your characteristics?"
    
    logger.info(f"[followup_node] Generated question: {question}")
    
    # PAUSE execution and wait for user answer
    user_answer = interrupt({
        "type": "follow_up_question",
        "question": question,
        "missing_areas": state.get("missing_areas", []),
        "iteration": state["iteration_count"],
        "confidence": state.get("confidence_score", 0.0)
    })
    
    # When resumed, user_answer contains their response
    logger.info(f"[followup_node] Received answer: {user_answer[:100] if isinstance(user_answer, str) else user_answer}...")
    
    # Update state and route back to questionnaire for re-analysis
    updated_answers = state.get("answers_collected", {}).copy()
    updated_answers[question] = str(user_answer)
    
    return Command(
        goto="questionnaire",
        update={
            "user_message": str(user_answer),  # Re-analyze with new answer
            "questions_asked": [question],  # Appends due to Annotated[List, add]
            "answers_collected": updated_answers,
            "iteration_count": state["iteration_count"] + 1
        }
    )


async def dosha_inference_node(state: DoshaGraphState) -> Dict[str, Any]:
    """Determine dosha composition from collected answers."""
    logger.info("[dosha_inference_node] Calculating dosha composition...")
    
    agent = DoshaInferenceAgent()
    
    # Get dosha inference
    result = await agent.infer_dosha(
        answers=state.get("answers_collected", {})
    )
    
    logger.info(
        f"[dosha_inference_node] Results: {result['dominant_dosha']} "
        f"(V:{result['vata_score']} P:{result['pitta_score']} K:{result['kapha_score']})"
    )
    
    return {
        "vata_score": result["vata_score"],
        "pitta_score": result["pitta_score"],
        "kapha_score": result["kapha_score"],
        "dominant_dosha": result["dominant_dosha"],
        "dosha_explanation": result["explanation"]
    }


async def response_generator_node(state: DoshaGraphState) -> Dict[str, Any]:
    """Generate comprehensive dosha assessment response."""
    logger.info("[response_generator_node] Generating assessment response...")
    
    llm_config = LLMConfig(model_name=OpenaiModels.GPT_4O_MINI.value, temperature=0.7)
    llm = llm_config.get_llm_instance()
    
    # Generate response
    prompt = RESPONSE_GENERATOR_PROMPT.format(
        vata_score=state.get("vata_score", 0),
        pitta_score=state.get("pitta_score", 0),
        kapha_score=state.get("kapha_score", 0),
        dominant_dosha=state.get("dominant_dosha", "Unknown"),
        explanation=state.get("dosha_explanation", "Assessment complete.")
    )
    
    try:
        response = await llm.ainvoke(prompt)
        generated_response = response.content.strip()
        
        logger.info(f"[response_generator_node] Generated response ({len(generated_response)} chars)")
        
        return {
            "final_response": generated_response,
            "next_action": "complete"
        }
        
    except Exception as e:
        logger.error(f"[response_generator_node] Error generating response: {e}")
        return {
            "final_response": f"""Based on your responses, your dominant dosha appears to be {state.get('dominant_dosha', 'Unknown')}.

Dosha Distribution:
- Vata: {state.get('vata_score', 0):.1f}%
- Pitta: {state.get('pitta_score', 0):.1f}%
- Kapha: {state.get('kapha_score', 0):.1f}%

{state.get('dosha_explanation', '')}

Please consult with an Ayurvedic practitioner for personalized guidance.""",
            "next_action": "complete"
        }

