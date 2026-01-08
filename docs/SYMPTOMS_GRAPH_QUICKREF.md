# Quick Reference: Symptoms Graph Phase 1

## Testing Locally

```bash
# Install dependencies (if not already)
pip install langgraph

# Test the graph directly
python examples/test_symptoms_graph.py

# Test via API
python -m app.main
# Then in another terminal:
curl -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d '{"message": "I have a headache"}'
```

## How Interrupts Work

### 1. Graph Pauses
```python
# In followup_node:
user_answer = interrupt({"question": "When did it start?"})
# ↑ Execution stops here, state saved, returns to caller
```

### 2. API Returns Question
```json
{
  "response": "When did it start?",
  "session_id": "session_abc",
  "active_graph": "symptoms_graph",
  "metadata": {
    "type": "follow_up_question",
    "missing_info": ["duration", "severity"]
  }
}
```

### 3. User Answers
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "3 days ago", "session_id": "session_abc"}'
```

### 4. Graph Resumes
```python
# In supervisor:
result = symptoms_graph.invoke(
    Command(resume="3 days ago"),  # User's answer
    config={"configurable": {"thread_id": "session_abc_symptoms"}}
)
# ↑ Execution continues from interrupt() point
```

## Key Files

| File | Purpose |
|------|---------|
| `app/graphs/symptoms_graph/state.py` | State definition (TypedDict) |
| `app/agents/symptom_triage_agent.py` | Extract structured symptoms |
| `app/agents/followup_agent.py` | Generate follow-up questions |
| `app/graphs/symptoms_graph/nodes.py` | symptom_triage, followup, response_generator nodes |
| `app/graphs/symptoms_graph/graph.py` | Build and compile LangGraph |
| `app/supervisor/supervisor_graph.py` | Invoke graph, handle pause/resume |

## Common Issues

### Issue: "ModuleNotFoundError: No module named 'langgraph'"
**Fix:** `pip install langgraph`

### Issue: Graph doesn't pause
**Check:** 
- Checkpointer is provided to `compile(checkpointer=...)`
- Thread ID is in config: `{"configurable": {"thread_id": "..."}}`

### Issue: Resume doesn't work
**Check:**
- Using same thread_id as initial invoke
- Using `Command(resume=value)` not just `value`

### Issue: LLM errors
**Check:**
- `OPENAI_API_KEY` is set in `.env`
- API key is valid and has credits

## State Flow

```
┌─────────────────────────────────────────┐
│ SessionState (Global)                   │
│ - session_id                            │
│ - messages                              │
│ - current_intent                        │
│ - active_graph                          │
│ - waiting_for_user_input  ← Pause flag │
└─────────────────────────────────────────┘
                  ↓ handoff
┌─────────────────────────────────────────┐
│ SymptomsGraphState (Local)              │
│ - user_message                          │
│ - structured_symptoms                   │
│ - questions_asked                       │
│ - answers_collected                     │
│ - needs_more_info                       │
│ - iteration_count                       │
│ - final_response                        │
└─────────────────────────────────────────┘
```

## Modifying Behavior

### Change max follow-ups:
```python
# In supervisor_graph.py:
input_state = {
    # ...
    "max_iterations": 5,  # Change from 3
    # ...
}
```

### Change LLM temperature:
```python
# In agents/*.py:
self.llm = LLMConfig.get_llm(temperature=0.5)  # Adjust as needed
```

### Switch to persistent checkpointer:
```python
# In app/graphs/symptoms_graph/graph.py:
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

checkpointer = SqliteSaver(sqlite3.connect("checkpoints.db"))
compiled_graph = workflow.compile(checkpointer=checkpointer)
```

## Example Conversation

```
User: I have a headache
Bot: When did your headache start?

User: 3 days ago
Bot: How severe is it? (mild/moderate/severe)

User: Moderate, in my forehead
Bot: Based on your moderate headache in the frontal region for 3 days, 
     here are my recommendations:
     
     1. Ensure adequate hydration (8 glasses of water daily)
     2. Get proper rest and sleep
     3. Avoid screen time when possible
     4. Consider over-the-counter pain relief if needed
     
     If symptoms persist beyond 5 days or worsen, please consult 
     a healthcare provider.
     
     DISCLAIMER: This is not medical advice...
```

## Debug Logging

All nodes log with `logger.info()`:
```
[symptom_triage_node] Processing message: I have a headache...
[symptom_triage_node] Extracted 1 symptoms, needs_more_info=True
[should_ask_followup] Routing to followup (iteration 0/3)
[followup_node] Generated question: When did your headache start?
[followup_node] Received answer: 3 days ago...
[symptom_triage_node] Processing message: 3 days ago...
[response_generator_node] Generating final response
[response_generator_node] Generated response (512 chars)
```

---

**Ready to use!** 🚀 Test with `python examples/test_symptoms_graph.py`
