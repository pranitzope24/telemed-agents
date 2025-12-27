# Graphs

## Overview

Graphs are specialized workflow pipelines that handle specific domain tasks. Each graph is a state machine with nodes representing processing steps. The supervisor routes requests to appropriate graphs based on user intent and risk level.

## Graph Architecture

Each graph consists of:
- **graph.py**: Defines the graph structure and node connections
- **nodes.py**: Implements individual processing nodes
- **state.py**: Defines graph-specific state models
- **prompts.py**: LLM prompts used by nodes

## Available Graphs

### 1. Symptoms Graph (`symptoms_graph/`)

**Purpose**: Collect, normalize, and triage user symptoms

**Nodes**:
1. **input_normalization_node**: Standardizes user symptom descriptions
2. **symptom_extraction_node**: Extracts structured symptom data (name, duration, severity, location)
3. **triage_node**: Uses `symptom_triage_agent` to assess urgency
4. **clarification_node**: Asks follow-up questions if needed (conditional loop)
5. **specialty_recommendation_node**: Suggests medical specialties
6. **safety_check_node**: Runs `emergency_detector` and `safety_agent`
7. **handoff_node**: Prepares data for next graph or supervisor

**State** (`SymptomsState`):
```python
{
  "raw_complaint": str,
  "normalized_complaint": str,
  "structured_symptoms": [{"name", "duration", "severity", "location"}],
  "triage_outcome": "needs_doctor" | "self_care" | "emergency",
  "suggested_specialties": [str],
  "clarification_needed": bool,
  "ayurveda_notes": str
}
```

**Flow**:
- User: "I have a headache for 3 days"
- → Normalize → Extract ("headache", "3 days", "moderate")
- → Triage → "needs_doctor"
- → Recommend specialty → "neurology"
- → Handoff to doctor_matching_graph or dosha_graph

**Emergency Handoff**: If triage detects high risk, immediately routes to `emergency_graph`

---

### 2. Dosha Graph (`dosha_graph/`)

**Purpose**: Ayurvedic constitution assessment through questionnaire

**Nodes**:
1. **questionnaire_start_node**: Initializes questionnaire
2. **question_node**: Presents next question from `questionnaire_agent`
3. **answer_collection_node**: Validates and stores user answer (loops back to question_node if more questions)
4. **dosha_calculation_node**: Uses `dosha_inference_agent` with Ayurveda RAG
5. **confidence_check_node**: If confidence < threshold, asks clarifying questions
6. **personalization_node**: Generates personalized Ayurvedic recommendations
7. **safety_validation_node**: Ensures recommendations are safe

**State** (`DoshaState`):
```python
{
  "answers": [{"question_id", "answer", "timestamp"}],
  "dosha_scores": {"vata": float, "pitta": float, "kapha": float},
  "dominant_dosha": str,
  "confidence": float,
  "current_question_index": int,
  "recommendations": [str]
}
```

**Flow**:
- User completes questionnaire (diet, sleep, digestion, etc.)
- → Calculate dosha scores using Ayurveda knowledge RAG
- → If confident, generate recommendations
- → Handoff to prescription_graph or return to supervisor

---

### 3. Doctor Matching Graph (`doctor_matching_graph/`)

**Purpose**: Find and book appropriate doctors

**Nodes**:
1. **specialty_mapping_node**: Maps symptoms to required specialties
2. **doctor_search_node**: Queries `doctor_service` with filters
3. **availability_check_node**: Checks real-time availability
4. **ranking_node**: Ranks doctors by relevance, ratings, distance
5. **presentation_node**: Shows top candidates to user
6. **selection_node**: Waits for user choice (pause point)
7. **booking_node**: Calls `booking_service` to create appointment
8. **confirmation_node**: Sends confirmation via `notification_service`

**State** (`DoctorMatchState`):
```python
{
  "required_specialties": [str],
  "search_filters": {"location", "insurance", "language"},
  "candidate_doctors": [{"id", "name", "specialty", "availability", "rating"}],
  "selected_doctor_id": str | None,
  "booking_status": "pending" | "confirmed" | "failed",
  "appointment_details": {"time", "location", "type"}
}
```

**Flow**:
- Input: suggested_specialties from symptoms_graph
- → Search doctors → Check availability → Rank
- → Present top 3 → User selects
- → Book appointment → Send confirmation

---

### 4. Prescription Graph (`prescription_graph/`)

**Purpose**: Draft, review, and approve prescriptions

**Nodes**:
1. **context_gathering_node**: Collects symptoms, dosha, doctor input
2. **draft_generation_node**: Uses `prescription_draft_agent` + Ayurveda RAG
3. **interaction_check_node**: Runs `drug_interaction_agent`
4. **safety_review_node**: `compliance_checker` validates prescription
5. **doctor_review_node**: Sends draft to doctor for approval (pause point)
6. **revision_node**: If doctor requests changes, loop back to draft
7. **pdf_generation_node**: Creates prescription PDF
8. **finalization_node**: Stores via `prescription_service`, sends to user

**State** (`PrescriptionState`):
```python
{
  "draft": str,
  "medications": [{"name", "dosage", "frequency", "duration"}],
  "interactions": [str],
  "contraindications": [str],
  "doctor_feedback": str | None,
  "revision_count": int,
  "approval_status": "draft" | "needs_changes" | "approved",
  "pdf_url": str | None
}
```

**Flow**:
- Input: symptoms + dosha profile + doctor notes
- → Draft prescription → Check interactions
- → Send to doctor → Doctor approves/requests changes
- → Generate PDF → Store and send to user

**Safety**: Multiple validation layers prevent unsafe prescriptions

---

### 5. Progress Graph (`progress_graph/`)

**Purpose**: Monitor treatment progress and recommend follow-ups

**Nodes**:
1. **log_collection_node**: Collects daily symptom logs from user
2. **aggregation_node**: Aggregates logs over time window
3. **trend_analysis_node**: Uses `trend_analysis_agent` to detect patterns
4. **comparison_node**: Compares against baseline and goals
5. **alert_check_node**: If worsening, generates doctor alert
6. **followup_recommendation_node**: Uses `followup_agent` for next steps
7. **notification_node**: Sends updates via `notification_service`

**State** (`ProgressState`):
```python
{
  "daily_logs": [{"date", "symptoms", "severity", "notes"}],
  "trend": "improving" | "stable" | "worsening" | "insufficient_data",
  "baseline": {"symptom_severity_map"},
  "current_metrics": {"symptom_severity_map"},
  "alerts": [str],
  "followup_plan": str,
  "next_checkin_date": date
}
```

**Flow**:
- User logs daily symptoms
- → Aggregate over 7 days → Analyze trend
- → If worsening, alert doctor
- → Generate follow-up recommendations

**Background Mode**: Can run as scheduled job to prompt users for logs

---

### 6. Emergency Graph (`emergency_graph/`)

**Purpose**: Handle emergency situations with immediate guidance

**Nodes**:
1. **emergency_classification_node**: Uses `emergency_response_agent` to classify severity
2. **immediate_guidance_node**: Provides first aid or stabilization instructions
3. **escalation_node**: Calls emergency services or redirects to ER
4. **safety_lock_node**: Locks other graphs, escalates to human
5. **audit_log_node**: Logs all actions for compliance

**State** (`EmergencyState`):
```python
{
  "trigger": str,
  "severity": "critical" | "urgent" | "false_alarm",
  "symptoms": [str],
  "actions_taken": [str],
  "escalated": bool,
  "emergency_contact_notified": bool
}
```

**Flow**:
- Triggered by high-risk classification or explicit emergency keywords
- → Classify severity → Provide immediate guidance
- → If critical, call emergency services
- → Lock session, escalate to human operator

**Priority**: Bypasses all other graphs; cannot be interrupted

---

## Graph Interaction Patterns

### Sequential Handoff
```
Symptoms → Dosha → Doctor Matching → Prescription → Progress
```
Typical happy path for comprehensive treatment.

### Conditional Branching
```
Symptoms → (if high-risk) → Emergency
          → (if self-care) → Dosha → Progress
          → (if needs-doctor) → Doctor Matching
```

### Parallel Execution
```
Symptoms ─┬→ Dosha Graph
          └→ Doctor Matching
```
Can run dosha assessment while searching for doctors.

### Loop-back
```
Prescription → Doctor Review → (needs changes) → Draft Generation (loop)
                             → (approved) → Finalization
```

### Pause/Resume
Graphs can pause at nodes waiting for:
- User input (questions, confirmations)
- External events (doctor approval, test results)
- Scheduled time (daily log reminders)

State is saved; graph resumes when input arrives.

---

## State Management in Graphs

### Global Session State
Shared across all graphs:
```python
SessionState = {
  "session_id": str,
  "intent": str,
  "active_graph": str,
  "active_node": str,
  "risk_level": str,
  "recent_turns": [messages],
  "handoff_data": dict,  # Data passed between graphs
  "profile_ref": str
}
```

### Per-Graph State
Each graph has isolated state slice (e.g., `SymptomsState`, `DoshaState`) stored separately in Redis.

### Handoff Data
When graph completes, it populates `handoff_data` with outputs for next graph:
```python
handoff_data = {
  "symptoms": [...],
  "dosha_profile": {...},
  "doctor_id": "...",
  "prescription_id": "..."
}
```

---

## Safety Integration

Every graph integrates safety checks:
1. **Pre-node**: Validate input, check for emergency keywords
2. **During LLM calls**: Hallucination detection, content filtering
3. **Post-node**: Compliance check, disclaimer injection
4. **Emergency detection**: Real-time monitoring across all nodes

---

## Testing Graphs

Each graph has corresponding test file in `tests/`:
- `test_symptoms_graph.py`: Unit tests for symptom nodes
- `test_dosha_graph.py`: Questionnaire flow tests
- `test_prescription_flow.py`: End-to-end prescription tests
- `test_emergency_flow.py`: Emergency detection tests

Use mocks for external services (`doctor_service`, `booking_service`, etc.)
