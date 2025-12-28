"""Doctor matching graph nodes - Simplified 3-node implementation."""

import json
import re
from typing import Dict, Any
from langgraph.types import Command, interrupt
from app.graphs.doctor_matching_graph.state import DoctorMatchingState
from app.graphs.doctor_matching_graph.prompts import (
    SPECIALTY_MAPPING_PROMPT,
    DOCTOR_PRESENTATION_PROMPT
)
from app.tools.doctor_service import search_doctors
from app.config.llm import LLMConfig
from app.constants.openai_constants import OpenaiModels
from app.utils.logger import get_logger

logger = get_logger()


async def symptoms_triage_node(state: DoctorMatchingState) -> Command:
    """Check if we have enough symptom context from handoff, global state, or conversation history.
    
    Priority:
    1. Handoff data (symptoms_summary, structured_symptoms)
    2. Conversation history (check recent messages for symptom mentions)
    3. Ask user if no symptoms found
    """
    logger.info("[symptoms_triage_node] Checking symptom context...")
    
    # 1. Check local state from handoff
    symptoms = state.get("symptoms_summary")
    structured_symptoms = state.get("structured_symptoms")
    
    if symptoms or structured_symptoms:
        logger.info(f"[symptoms_triage_node] Have symptoms from {state.get('handoff_source', 'unknown')}")
        return Command(goto="specialty_recommendation")
    
    # 2. Check conversation history from state (passed via session_context)
    session_context = state.get("session_context", {})
    reported_symptoms_list = session_context.get("reported_symptoms", [])
    recent_messages = session_context.get("recent_messages", [])
    
    # If we have reported symptoms from previous graphs
    if reported_symptoms_list:
        symptoms_summary = ", ".join(reported_symptoms_list)
        logger.info(f"[symptoms_triage_node] Found symptoms in session history: {symptoms_summary}")
        return Command(
            goto="specialty_recommendation",
            update={
                "symptoms_summary": symptoms_summary,
                "handoff_source": "session_history"
            }
        )
    
    # If we have recent conversation mentioning symptoms
    if recent_messages:
        # Extract symptom mentions from all messages (both user and assistant)
        combined_messages = []
        for msg in recent_messages[-10:]:  # Check last 10 messages
            content = msg.get("content", "")
            role = msg.get("role", "")
            combined_messages.append(f"{role}: {content}")
        
        combined_text = " ".join(combined_messages)
        
        # Extended keyword check for symptom mentions
        symptom_keywords = [
            "pain", "fever", "headache", "cough", "cold", "sick", "hurt", "ache", 
            "problem", "issue", "symptom", "feel", "temperature", "throat", "stomach",
            "nausea", "dizzy", "tired", "fatigue", "rash", "itch", "sore", "burning",
            "swelling", "bleeding", "vomit", "diarrhea", "constipation", "anxiety",
            "stress", "sleep", "appetite", "weight", "breathing", "chest", "back",
            "joint", "muscle", "weakness", "numbness"
        ]
        
        if any(keyword in combined_text.lower() for keyword in symptom_keywords):
            # Extract user's actual symptom description (prefer user messages)
            user_symptom_messages = []
            for msg in recent_messages:
                if msg.get("role") == "user":
                    content = msg.get("content", "").lower()
                    if any(kw in content for kw in symptom_keywords):
                        user_symptom_messages.append(msg.get("content", ""))
            
            if user_symptom_messages:
                symptoms_text = ". ".join(user_symptom_messages[-3:])  # Last 3 symptom mentions
                logger.info(f"[symptoms_triage_node] Found symptoms in conversation: {symptoms_text[:100]}...")
                return Command(
                    goto="specialty_recommendation",
                    update={
                        "symptoms_summary": symptoms_text[:800],  # Increased limit for better context
                        "handoff_source": "conversation_history"
                    }
                )
    
    # 3. No symptoms found anywhere, ask user
    logger.info("[symptoms_triage_node] No symptoms found in history, asking user")
    
    user_answer = interrupt({
        "type": "symptoms_question",
        "question": "What symptoms or health concerns are you experiencing? Please describe your condition so I can recommend the right specialist."
    })
    
    return Command(
        goto="specialty_recommendation",
        update={
            "symptoms_summary": str(user_answer),
            "user_message": str(user_answer),
            "handoff_source": "direct"
        }
    )


async def specialty_recommendation_node(state: DoctorMatchingState) -> Command:
    """Map symptoms to Ayurvedic specialties and collect location.
    
    Steps:
    1. Use LLM to map symptoms → specialties
    2. Present recommendation with explanation
    3. Ask for city (in same question)
    4. Parse city from response
    """
    logger.info("[specialty_recommendation_node] Mapping symptoms to specialties...")
    
    # Get LLM
    llm_config = LLMConfig(model_name=OpenaiModels.GPT_4O_MINI.value, temperature=0.3)
    llm = llm_config.get_llm_instance()
    
    # Build symptoms context
    symptoms = state.get("symptoms_summary", "")
    structured_symptoms = state.get("structured_symptoms", [])
    
    additional_context = ""
    if structured_symptoms:
        additional_context = "Detailed symptoms:\n"
        for symp in structured_symptoms:
            name = symp.get('name', 'Unknown')
            severity = symp.get('severity', '')
            duration = symp.get('duration', '')
            additional_context += f"- {name}"
            if severity:
                additional_context += f" (Severity: {severity})"
            if duration:
                additional_context += f" (Duration: {duration})"
            additional_context += "\n"
    
    # Map to specialties using LLM
    prompt = SPECIALTY_MAPPING_PROMPT.format(
        symptoms_summary=symptoms,
        additional_context=additional_context or "(None)"
    )
    
    try:
        response = await llm.ainvoke(prompt)
        content = response.content.strip()
        
        # Parse JSON
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        result = json.loads(content)
        specialties = result.get("specialties", ["General Ayurveda"])
        explanation = result.get("explanation", "Based on your symptoms, I recommend consulting an Ayurvedic specialist.")
        
        logger.info(f"[specialty_recommendation_node] Mapped to: {specialties}")
        
    except Exception as e:
        logger.error(f"[specialty_recommendation_node] Error mapping specialties: {e}")
        specialties = ["General Ayurveda"]
        explanation = "I recommend consulting a General Ayurveda specialist for your condition."
    
    # Present recommendation and ask for location
    specialties_text = " or ".join(specialties)
    question = f"""Based on your symptoms, I recommend consulting:

🩺 **{specialties_text}**

{explanation}

To find available doctors, please tell me which city you're in (e.g., Delhi, Mumbai, Bangalore)."""
    
    user_answer = interrupt({
        "type": "specialty_and_location",
        "question": question,
        "suggested_specialties": specialties
    })
    
    # Extract city from answer
    city = _extract_city(str(user_answer))
    
    if not city:
        # Couldn't parse city, ask again more directly
        logger.warning(f"[specialty_recommendation_node] Could not parse city from: {user_answer}")
        
        follow_up = interrupt({
            "type": "city_clarification",
            "question": "I couldn't identify the city. Please provide just the city name (e.g., Delhi, Mumbai, Pune)."
        })
        
        city = _extract_city(str(follow_up))
        
        if not city:
            # Still can't parse, use default or ask one more time
            logger.error(f"[specialty_recommendation_node] Still can't parse city from: {follow_up}")
            city = "Delhi"  # Default fallback
    
    logger.info(f"[specialty_recommendation_node] Extracted city: {city}")
    
    return Command(
        goto="doctor_search",
        update={
            "confirmed_specialties": specialties,
            "user_location_city": city
        }
    )


def _extract_city(text: str) -> str:
    """Extract city name from user input.
    
    Simple pattern matching for common Indian cities.
    """
    text_lower = text.lower()
    
    # Common Indian cities
    cities = [
        "delhi", "mumbai", "bangalore", "bengaluru", "hyderabad", "chennai",
        "kolkata", "pune", "ahmedabad", "jaipur", "surat", "lucknow",
        "kanpur", "nagpur", "indore", "thane", "bhopal", "visakhapatnam",
        "pimpri", "patna", "vadodara", "ghaziabad", "ludhiana", "agra",
        "nashik", "faridabad", "meerut", "rajkot", "varanasi", "srinagar",
        "aurangabad", "dhanbad", "amritsar", "navi mumbai", "allahabad",
        "ranchi", "howrah", "coimbatore", "jabalpur", "gwalior", "vijayawada",
        "jodhpur", "madurai", "raipur", "kota", "guwahati", "chandigarh",
        "solapur", "hubli", "dharwad", "mysore", "bareilly", "moradabad"
    ]
    
    # Check for exact match
    for city in cities:
        if city in text_lower:
            return city.title()
    
    # Try to extract capitalized words (likely city names)
    words = text.split()
    for word in words:
        if word.istitle() and len(word) > 3:
            return word
    
    return ""


async def doctor_search_node(state: DoctorMatchingState) -> Dict[str, Any]:
    """Search for doctors and present results.
    
    This is the final node - returns dict to END the graph.
    UI will handle booking flow with buttons.
    """
    logger.info("[doctor_search_node] Searching for doctors...")
    
    specialties = state.get("confirmed_specialties", [])
    city = state.get("user_location_city", "")
    
    # Search doctors via API
    try:
        result = await search_doctors(
            specialties=specialties,
            city=city
        )
        
        doctors = result.get("doctors", [])
        
        if not doctors:
            logger.warning(f"[doctor_search_node] No doctors found for {specialties} in {city}")
            return {
                "final_response": f"I couldn't find any {', '.join(specialties)} specialists in {city} right now. Would you like to try a different city or specialty?",
                "next_action": "complete",
                "available_doctors": []
            }
        
        logger.info(f"[doctor_search_node] Found {len(doctors)} doctors")
        
        # Convert DoctorInfo objects to dictionaries
        top_doctors = doctors[:3]
        top_doctors_dicts = [doc.to_dict() for doc in top_doctors]
        
        # Format response using LLM
        llm_config = LLMConfig(model_name=OpenaiModels.GPT_4O_MINI.value, temperature=0.7)
        llm = llm_config.get_llm_instance()
        
        doctors_json = json.dumps(top_doctors_dicts, indent=2)
        prompt = DOCTOR_PRESENTATION_PROMPT.format(doctors_json=doctors_json)
        
        response = await llm.ainvoke(prompt)
        formatted_response = response.content.strip()
        
        logger.info("[doctor_search_node] Successfully formatted doctor presentation")
        
        return {
            "final_response": formatted_response,
            "next_action": "complete",
            "available_doctors": top_doctors_dicts,
            "booking_context": {
                "symptoms": state.get("symptoms_summary"),
                "structured_symptoms": state.get("structured_symptoms"),
                "specialties": specialties,
                "city": city
            }
        }
        
    except Exception as e:
        logger.error(f"[doctor_search_node] Error: {e}")
        return {
            "final_response": "I'm having trouble searching for doctors right now. Please try again in a moment.",
            "next_action": "complete",
            "available_doctors": []
        }
