"""Doctor matching graph nodes - Simplified 2-node flow."""

import json
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from app.graphs.doctor_matching_graph.state import DoctorMatchingState
from app.graphs.doctor_matching_graph.prompts import (
    SPECIALTY_MAPPING_PROMPT,
    DOCTOR_SEARCH_PROMPT
)
from app.tools.doctor_service import search_doctors as search_doctors_api
from app.config.llm import LLMConfig
from app.constants.openai_constants import OpenaiModels
from app.utils.logger import get_logger

logger = get_logger()


# ===== Tool Definition =====

@tool
async def search_doctors_tool(
    specialties: List[str],
    city: str,
    min_rating: float = 4.0
) -> Dict[str, Any]:
    """Search for Ayurvedic doctors by specialty and location.
    
    Args:
        specialties: List of Ayurvedic specialties to search for (e.g., ["Panchakarma", "General Ayurveda"])
        city: City name to search in (e.g., "Delhi", "Mumbai")
        min_rating: Minimum doctor rating filter (default: 4.0)
    
    Returns:
        Dictionary with doctors list and count
    """
    logger.info(f"[search_doctors_tool] Searching for {specialties} in {city}")
    
    try:
        result = await search_doctors_api(
            specialties=specialties,
            city=city,
            min_rating=min_rating
        )
        
        doctors = result.get("doctors", [])
        
        if not doctors:
            return {
                "doctors": [],
                "count": 0,
                "message": f"No doctors found for {', '.join(specialties)} in {city}"
            }
        
        # Convert DoctorInfo objects to dicts
        doctors_list = [doc.to_dict() for doc in doctors[:5]]  # Top 5
        
        return {
            "doctors": doctors_list,
            "count": len(doctors_list),
            "message": f"Found {len(doctors_list)} doctors"
        }
        
    except Exception as e:
        logger.error(f"[search_doctors_tool] Error: {e}")
        return {
            "doctors": [],
            "count": 0,
            "error": str(e)
        }


# ===== Pydantic Models for Structured Output =====

class SpecialtyMapping(BaseModel):
    """Structured output from specialty mapping."""
    specialties: List[str] = Field(description="Recommended Ayurvedic specialties (1-2)")
    explanation: str = Field(description="Brief explanation for the patient")


# ===== Node 1: Specialty Mapper =====

async def specialty_mapper_node(state: DoctorMatchingState) -> Dict[str, Any]:
    """Map symptoms to Ayurvedic specialties using handoff data.
    
    Receives structured symptoms from symptoms graph handoff.
    """
    logger.info("[specialty_mapper_node] Mapping symptoms to specialties...")
    
    # Get data from handoff
    structured_symptoms = state.get("structured_symptoms", [])
    symptoms_summary = state.get("symptoms_summary", "")
    
    # Build detailed symptoms string
# ===== Node 2: Doctor Search (LLM with Tool Calling) =====

async def doctor_search_node(state: DoctorMatchingState) -> Dict[str, Any]:
    """Search for doctors using LLM with tool calling capability.
    
    The LLM will:
    1. Use search_doctors_tool to find doctors
    2. Generate a personalized response with specialty recommendation
    3. Present the doctor list in a friendly format
    """
    logger.info("[doctor_search_node] Starting LLM-based doctor search...")
    
    specialties = state.get("recommended_specialties", [])
    specialty_explanation = state.get("specialty_explanation", "")
    structured_symptoms = state.get("structured_symptoms", [])
    
    # Get city from session context
    session_context = state.get("session_context", {})
    city = session_context.get("user_location_city", "")
    
    if not city:
        logger.warning("[doctor_search_node] No city in session context, using default: Delhi")
        city = "Delhi"
    
    # Build symptoms summary for context
    symptoms_summary = ""
    if structured_symptoms:
        symptom_names = [s.get('name', '') for s in structured_symptoms if s.get('name')]
        symptoms_summary = ", ".join(symptom_names)
    
    logger.info(f"[doctor_search_node] Specialties: {specialties}, City: {city}")
    
    # Create LLM with tool binding
    llm_config = LLMConfig(model_name=OpenaiModels.GPT_4O.value, temperature=0.7)
    llm = llm_config.get_llm_instance()
    llm_with_tools = llm.bind_tools([search_doctors_tool])
    
    # Build prompt for LLM
    specialties_text = ", ".join(specialties)
    prompt = DOCTOR_SEARCH_PROMPT.format(
        specialties=specialties_text,
        specialty_explanation=specialty_explanation,
        symptoms=symptoms_summary or "general consultation",
        city=city
    )
    
    logger.info(f"[doctor_search_node] Invoking LLM with tool calling...")
    
    try:
        # Invoke LLM (it will call the tool if needed)
        response = await llm_with_tools.ainvoke(prompt)
        
        # Check if LLM called the tool
        doctors_list = []
        if hasattr(response, 'tool_calls') and response.tool_calls:
            logger.info(f"[doctor_search_node] LLM made {len(response.tool_calls)} tool call(s)")
            
            # Execute tool calls
            for tool_call in response.tool_calls:
                if tool_call['name'] == 'search_doctors_tool':
                    tool_result = await search_doctors_tool.ainvoke(tool_call['args'])
                    doctors_list = tool_result.get('doctors', [])
                    logger.info(f"[doctor_search_node] Tool returned {len(doctors_list)} doctors")
            
            # If we have doctors, ask LLM to format the final response
            if doctors_list:
                doctors_json = json.dumps(doctors_list, indent=2)
                final_prompt = f"""{prompt}

The search found these doctors:
{doctors_json}

Now provide your complete response including:
1. Specialty recommendation with explanation
2. Brief overview of the doctors found
3. End with: "You can view the complete list of doctors and book an appointment using the button below."

Keep it conversational and helpful."""
                
                final_response = await llm.ainvoke(final_prompt)
                formatted_text = final_response.content.strip()
            else:
                formatted_text = f"I couldn't find any {specialties_text} specialists in {city} right now. Would you like to try a different city or specialty?"
        else:
            # LLM responded without calling tool (fallback)
            logger.warning("[doctor_search_node] LLM did not call tool, using direct response")
            formatted_text = response.content.strip()
            
            # Try to search anyway as fallback
            try:
                tool_result = await search_doctors_tool.ainvoke({
                    "specialties": specialties,
                    "city": city,
                    "min_rating": 4.0
                })
                doctors_list = tool_result.get('doctors', [])
            except Exception as e:
                logger.error(f"[doctor_search_node] Fallback search failed: {e}")
        
        logger.info(f"[doctor_search_node] Final response generated with {len(doctors_list)} doctors")
        
        return {
            "final_response": formatted_text,
            "next_action": "complete",
            "available_doctors": doctors_list,
            "doctor_search_results": doctors_list,
            "booking_context": {
                "symptoms": structured_symptoms,
                "specialties": specialties,
                "city": city
            }
        }
        
    except Exception as e:
        logger.error(f"[doctor_search_node] Error in LLM tool calling: {e}")
        
        # Fallback: direct response
        return {
            "final_response": f"Based on your symptoms, I recommend consulting a {', '.join(specialties)} specialist in {city}. However, I'm having trouble accessing the doctor database right now. Please try again in a moment.",
            "next_action": "complete",
            "available_doctors": [],
            "doctor_search_results": [],
            "booking_context": {
                "symptoms": structured_symptoms,
                "specialties": specialties,
                "city": city
            }
        }
