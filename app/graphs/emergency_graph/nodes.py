"""Emergency graph nodes implementation."""

from typing import Any, Dict, List

from app.config.llm import LLMConfig
from app.constants.openai_constants import OpenaiModels
from app.graphs.emergency_graph.prompts import EMERGENCY_FIRST_AID_PROMPT
from app.graphs.emergency_graph.state import EmergencyGraphState
from app.safety.compliance_checker import SafetyComplianceChecker
from app.supervisor.risk_classifier import classify_risk
from app.utils.logger import get_logger

logger = get_logger()


def _infer_emergency_type(message: str, keywords: List[str]) -> str:
	"""Infer emergency type from detected keywords and message content."""
	text = message.lower()
	kw = [k.lower() for k in keywords]

	def has(*terms):
		return any(t in text or t in kw for t in terms)

	if has("chest pain", "heart attack"):
		return "cardiac"
	if has("can't breathe", "cannot breathe", "difficulty breathing", "choking"):
		return "respiratory"
	if has("bleeding heavily", "severe bleeding"):
		return "bleeding"
	if has("stroke", "seizure", "paralyzed", "lost consciousness", "unconscious"):
		return "neurological"
	if has("anaphylaxis", "allergic reaction severe"):
		return "allergic"
	if has("severe burn"):
		return "burn"
	if has("overdose"):
		return "overdose"
	if has("suicide", "suicidal"):
		return "suicidal_ideation"
	if has("extreme pain"):
		return "extreme_pain"
	return "unknown"


async def classify_emergency_intent(state: EmergencyGraphState) -> Dict[str, Any]:
	"""Classify risk and emergency type from user message."""
	message = state.get("user_message", "")
	logger.info("[classify_emergency_intent] Classifying risk for message...")

	result = await classify_risk(message)

	risk_level = result.get("risk_level", "medium")
	keywords = result.get("emergency_keywords", [])
	urgency = float(result.get("urgency_score", 0.5))
	needs_911 = risk_level == "emergency"

	emergency_type = _infer_emergency_type(message, keywords)
	incident_summary = message[:160]

	logger.info(
		f"[classify_emergency_intent] risk={risk_level} type={emergency_type} 911={needs_911}"
	)

	return {
		"incident_summary": incident_summary,
		"risk_level": risk_level,
		"detected_keywords": keywords,
		"urgency_score": urgency,
		"needs_911": needs_911,
		"emergency_type": emergency_type,
	}


def _first_aid_for_type(emergency_type: str) -> str:
	"""Return concise, general first-aid guidance for the type."""
	templates = {
		"cardiac": (
			"Immediate actions:\n"
			"- Call emergency services (112) or ambulance (108) now.\n"
			"- Sit or lie down; avoid exertion.\n"
			"- Loosen tight clothing; monitor breathing.\n"
			"- If the person collapses and isn't breathing, begin CPR if trained."
		),
		"respiratory": (
			"Immediate actions:\n"
			"- Call emergency services (112) or ambulance (108).\n"
			"- Sit upright; focus on slow, steady breaths.\n"
			"- If choking and trained, perform abdominal thrusts.\n"
			"- Use prescribed inhaler or device if available."
		),
		"bleeding": (
			"Immediate actions:\n"
			"- Call emergency services (112) or ambulance (108).\n"
			"- Apply firm, direct pressure with a clean cloth.\n"
			"- Elevate the limb if no fracture suspected.\n"
			"- Do not remove deeply embedded objects."
		),
		"neurological": (
			"Immediate actions:\n"
			"- Call emergency services (112) or ambulance (108).\n"
			"- Stroke signs: note the time symptoms started, keep the person safe, no food/drink.\n"
			"- Seizure: clear the area, place in recovery position, do not restrain, do not put anything in the mouth."
		),
		"allergic": (
			"Immediate actions:\n"
			"- Call emergency services (112) or ambulance (108).\n"
			"- Use prescribed epinephrine auto-injector immediately if available.\n"
			"- Lie down and raise legs; avoid triggers."
		),
		"burn": (
			"Immediate actions:\n"
			"- Call emergency services (112) or ambulance (108) for severe burns.\n"
			"- Cool the burn under cool running water for 10–20 minutes.\n"
			"- Do not use ice or creams; cover with a clean cloth."
		),
		"overdose": (
			"Immediate actions:\n"
			"- Call emergency services (112) or ambulance (108).\n"
			"- Do not leave the person alone; monitor breathing.\n"
			"- If trained and available, administer naloxone.\n"
			"- Place in recovery position if drowsy or vomiting."
		),
		"suicidal_ideation": (
			"Immediate actions:\n"
			"- Call emergency services (112) or ambulance (108).\n"
			"- In India, you can contact the national mental health helpline 'Kiran' at 1800-599-0019, or local suicide prevention helplines.\n"
			"- Stay with the person; remove access to dangerous items.\n"
			"- Seek urgent support from a trusted person or professional."
		),
		"extreme_pain": (
			"Immediate actions:\n"
			"- Call emergency services (112) or ambulance (108).\n"
			"- Rest; avoid food and drink until assessed.\n"
			"- Monitor for worsening symptoms."
		),
		"unknown": (
			"Immediate actions:\n"
			"- Call emergency services (112) or ambulance (108).\n"
			"- Keep the person safe; monitor breathing and consciousness.\n"
			"- Avoid food or drink; prepare for transport."
		),
	}
	return templates.get(emergency_type, templates["unknown"])


async def generate_first_aid_response(state: EmergencyGraphState) -> Dict[str, Any]:
	"""Generate a concise first-aid response using LLM with safe fallback."""
	emergency_type = state.get("emergency_type", "unknown")
	logger.info(f"[generate_first_aid_response] Generating first-aid for type={emergency_type}")

	try:
		# Prepare LLM
		llm_config = LLMConfig(model_name=OpenaiModels.GPT_4O_MINI.value, temperature=0.2)
		llm = llm_config.get_llm_instance()

		# Build prompt
		prompt = EMERGENCY_FIRST_AID_PROMPT.format(
			incident_summary=state.get("incident_summary", ""),
			emergency_type=emergency_type,
			risk_level=state.get("risk_level", "unknown"),
			keywords=", ".join(state.get("detected_keywords", [])) or "none",
		)

		response = await llm.ainvoke(prompt)
		text = response.content.strip()
		first_aid_text = text
	except Exception as e:
		logger.error(f"[generate_first_aid_response] LLM error, using fallback: {e}")
		first_aid_text = (
			f"\n\n⚠️ MEDICAL EMERGENCY DETECTED\nCategory: {emergency_type.replace('_',' ').title()}\n\n"
			f"{_first_aid_for_type(emergency_type)}\n"
			f"\nIf you are alone, put the phone on speaker while calling 112/108. Follow operator instructions and do not delay seeking care.\n"
			f"\n🚨 Seek immediate medical attention. This assistant cannot provide emergency care.\n"
		)

	return {
		"first_aid_instructions": first_aid_text,
		"escalation_advice": "Seek immediate medical attention.",
		"final_response": first_aid_text,
		"needs_911": True if state.get("risk_level") == "emergency" else state.get("needs_911", False),
	}


async def finalize_and_end(state: EmergencyGraphState) -> Dict[str, Any]:
	"""Apply safety compliance checks and finish the flow."""
	logger.info("[finalize_and_end] Running safety compliance and completing flow")
	checker = SafetyComplianceChecker()

	context = {
		"incident_summary": state.get("incident_summary", ""),
		"emergency_type": state.get("emergency_type", "unknown"),
		"risk_level": state.get("risk_level", "medium"),
		"keywords": state.get("detected_keywords", []),
	}

	safety_result = checker.check_response(
		response=state.get("final_response", ""),
		context=context,
	)

	logger.info(
		f"[finalize_and_end] Flags={len(safety_result['safety_flags'])} Escalation={safety_result['needs_escalation']}"
	)

	return {
		"final_response": safety_result["final_response"],
		"safety_flags": safety_result["safety_flags"],
		"next_action": "complete",
		"completed": True,
	}
