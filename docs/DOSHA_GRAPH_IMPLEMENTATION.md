# Dosha Graph - Implementation Guide

## ✅ Implementation Complete

The dosha assessment graph has been implemented following the same patterns as the symptoms graph.

## 🏗️ Architecture

### Flow Diagram
```
START
  ↓
questionnaire_node (analyzes responses + calculates confidence)
  ↓
should_ask_followup? (confidence < 0.7?)
  ↓ YES                           ↓ NO
followup_node                 dosha_inference_node
  ↓ (interrupt)                   ↓
  ↓ (loops back)             response_generator_node
  ↓                               ↓
  └──────────→              safety_compliance_node
                                  ↓
                                 END
```

## 📁 Files Created/Updated

### 1. State (`app/graphs/dosha_graph/state.py`)
- `DoshaGraphState` - TypedDict with all required fields
- Tracks: answers, confidence, scores, iterations, output

### 2. Agents

#### `DoshaQuestionnaireAgent` (`app/agents/questionnaire_agent.py`)
- Analyzes user responses
- Calculates confidence score (0.0 to 1.0)
- Identifies missing areas
- **Required areas**: body_type, digestion, sleep_pattern, temperament, skin_type, energy_level

#### `DoshaInferenceAgent` (`app/agents/dosha_inference_agent.py`)
- LLM-based dosha calculation
- Returns Vata, Pitta, Kapha scores (0-100)
- Determines dominant dosha
- Provides explanation

### 3. Safety (`app/safety/compliance_checker.py`)
- `SafetyComplianceChecker` class
- Adds medical disclaimers
- Flags concerning keywords
- Validates dosha data integrity

### 4. Nodes (`app/graphs/dosha_graph/nodes.py`)

| Node | Purpose | Returns |
|------|---------|---------|
| `questionnaire_node` | Analyze responses, calculate confidence | State updates |
| `followup_node` | Generate questions, use interrupt() | Command |
| `dosha_inference_node` | Calculate dosha scores | Scores + dominant |
| `response_generator_node` | Format results nicely | Final response |
| `safety_compliance_node` | Add disclaimers, validate | Safe response |

### 5. Graph (`app/graphs/dosha_graph/graph.py`)
- Built with StateGraph
- Conditional edge: `should_ask_followup()`
- Compiled with MemorySaver checkpointer
- Singleton: `dosha_graph`

### 6. Prompts (`app/graphs/dosha_graph/prompts.py`)
- Questionnaire analysis prompt
- Follow-up question generator
- Response formatting prompt
- Includes Ayurveda knowledge

## 🎯 Key Features

### Confidence-Based Flow
- **Threshold**: 0.7 (70% confidence)
- Confidence = covered_areas / total_required_areas
- If confidence < 0.7 → ask follow-up
- If confidence >= 0.7 → proceed to inference

### Interrupt/Resume Pattern
Same as symptoms graph:
```python
# In followup_node:
user_answer = interrupt({
    "type": "follow_up_question",
    "question": question,
    "confidence": confidence_score
})
```

### Safety Checks
- Validates dosha scores (0-100, sum ~100)
- Adds Ayurveda disclaimer
- Flags medical concerns
- Escalates if needed

## 🧪 Testing

Run the test script:
```bash
python examples/test_dosha_graph.py
```

This tests:
1. **Multi-turn conversation** - Progressive question asking
2. **Single-turn** - Comprehensive initial info

## 📊 Example Usage

### Initial Invocation
```python
from app.graphs.dosha_graph.graph import dosha_graph

initial_state = {
    "user_message": "I want to know my dosha",
    "session_id": "session_123",
    "answers_collected": {},
    "confidence_score": 0.0,
    "confidence_threshold": 0.7,
    "questions_asked": [],
    "needs_more_info": True,
    "missing_areas": [],
    "iteration_count": 0,
    "max_iterations": 5,
    # ... other fields with None/[]
}

config = {"configurable": {"thread_id": "session_123_dosha"}}
result = await dosha_graph.ainvoke(initial_state, config)
```

### Handle Interrupt
```python
if result.get("__interrupt__"):
    question = result["__interrupt__"][0].value["question"]
    # Show question to user, get answer
    
    # Resume
    result = await dosha_graph.ainvoke(
        Command(resume=user_answer),
        config
    )
```

## 🔗 Supervisor Integration

✅ **INTEGRATED** - The dosha graph is now fully integrated with the supervisor.

### How it works:

1. **Intent Detection**: When user mentions dosha-related keywords, supervisor classifies intent as "dosha"
2. **Routing**: Supervisor routes to `dosha_graph` 
3. **Execution**: Graph starts with initial state
4. **Pause/Resume**: 
   - Graph pauses with `interrupt()` when confidence < 0.7
   - Supervisor saves state and returns question to user
   - User answer resumes the graph with `Command(resume=answer)`
5. **Completion**: Final response with dosha scores returned to user

### Supervisor Changes Made:

**File: `app/supervisor/supervisor_graph.py`**

Added:
- ✅ Resume handler for `dosha_graph` (similar to symptoms_graph)
- ✅ Initial invocation with proper state initialization
- ✅ Interrupt handling (pause and return question)
- ✅ Completion handling (return results with metadata)
- ✅ Thread ID: `{session_id}_dosha` for persistence

### Example Flow:

```python
# User: "I want to know my dosha type"
# Supervisor classifies intent = "dosha"
# Supervisor routes to dosha_graph

# Initial invocation:
result = await dosha_graph.ainvoke(initial_state, config)

# If interrupt:
# → Return question to user
# → Wait for answer

# User provides answer
# → Supervisor calls: dosha_graph.ainvoke(Command(resume=answer), config)

# Repeat until confidence >= 0.7
# → Then proceed to inference → response → safety → complete
```

### Metadata Returned:

**On Pause:**
```json
{
  "action": "paused",
  "graph": "dosha_graph",
  "response": "How would you describe your skin type?",
  "metadata": {
    "type": "follow_up_question",
    "missing_areas": ["skin_type", "energy_level"],
    "confidence": 0.5,
    "iteration": 2
  }
}
```

**On Completion:**
```json
{
  "action": "completed",
  "graph": "dosha_graph",
  "response": "Based on your assessment...[full response with disclaimers]",
  "metadata": {
    "vata_score": 65.0,
    "pitta_score": 25.0,
    "kapha_score": 10.0,
    "dominant_dosha": "Vata",
    "safety_flags": [],
    "next_action": "complete"
  }
}
```

---

**Status**: ✅ **Fully integrated with supervisor and ready for testing**

## 📋 Required Areas for Assessment

1. **Body Type**: Frame, build, weight patterns
2. **Digestion**: Appetite, metabolism, food preferences
3. **Sleep Pattern**: Quality, duration, ease of sleep
4. **Temperament**: Energy, emotions, stress response
5. **Skin Type**: Dry, oily, sensitive
6. **Energy Level**: Consistent, variable, steady

## 🎨 Dosha Characteristics (Built into prompts)

### Vata (Air + Space)
- Thin/light frame, dry skin
- Variable appetite, light sleep
- Creative, quick mind, anxious

### Pitta (Fire + Water)
- Medium build, warm body
- Strong appetite, sharp digestion
- Focused, intense, competitive

### Kapha (Earth + Water)
- Heavy/solid build, smooth skin
- Slow digestion, deep sleep
- Calm, patient, steady

## 🚀 Next Steps

1. **Test the graph**: Run `python examples/test_dosha_graph.py`
2. **Integrate with supervisor**: Add routing for "dosha" intent
3. **Add RAG later**: Replace simple LLM prompts with RAG-enhanced knowledge
4. **Tune confidence threshold**: Adjust based on real usage
5. **Expand questionnaire**: Add more nuanced questions if needed

## 🔄 Comparison with Symptoms Graph

| Feature | Symptoms Graph | Dosha Graph |
|---------|---------------|-------------|
| State tracking | ✅ TypedDict | ✅ TypedDict |
| Confidence-based | needs_more_info | confidence_score |
| Follow-up pattern | ✅ interrupt() | ✅ interrupt() |
| Max iterations | 3 | 5 |
| Final validation | Basic | ✅ Safety + Compliance |
| Output | General advice | Dosha scores + guidance |

## ⚠️ Important Notes

- Currently uses **LLM-based inference** with basic Ayurveda knowledge
- **RAG integration planned** for future (will enhance accuracy)
- Confidence threshold set to **0.7** (can be adjusted)
- Max iterations: **5** (balances thoroughness vs. user patience)
- All responses include **medical disclaimers**
- Safety checker validates dosha data integrity

---

**Status**: ✅ Ready for testing and supervisor integration
**Pattern**: Follows symptoms_graph architecture exactly
**Simplicity**: Kept simple as requested, no over-engineering
