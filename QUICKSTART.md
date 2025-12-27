# Quick Start: Supervisor System

## Setup (2 minutes)

1. **Configure environment:**
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key:
# OPENAI_API_KEY=sk-your-actual-key-here
```

2. **Start the server:**
```bash
python -m app.main
```

3. **Test it:**
```bash
# Simple symptom check
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I have a headache"}'

# Emergency test
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I am having severe chest pain"}'
```

## What It Does

**Every message goes through:**
1. ✅ **Risk Classification** → Detects emergencies & assesses urgency
2. ✅ **Intent Classification** → Determines what user wants
3. ✅ **Routing** → Selects appropriate specialized graph
4. ✅ **Response** → Returns mock response (graphs not yet implemented)

## Response Structure

```json
{
  "response": "Bot message",
  "session_id": "session_abc",
  "intent": "symptom|dosha|doctor|prescription|progress|emergency|general",
  "risk_level": "low|medium|high|emergency",
  "active_graph": "symptoms_graph|dosha_graph|...",
  "warning": "⚠️ EMERGENCY DETECTED..." // Only for emergencies,
  "metadata": {
    "intent_confidence": 0.85,
    "intent_reasoning": "...",
    "risk_reasoning": "...",
    "urgency_score": 0.4
  }
}
```

## Intent Types

| User Says | Intent | Routes To |
|-----------|--------|-----------|
| "I have a fever" | `symptom` | `symptoms_graph` |
| "What's my dosha?" | `dosha` | `dosha_graph` |
| "Book appointment" | `doctor` | `doctor_matching_graph` |
| "Refill prescription" | `prescription` | `prescription_graph` |
| "Track my progress" | `progress` | `progress_graph` |
| "I can't breathe" | `emergency` | `emergency_graph` |
| "Tell me about health" | `general` | `symptoms_graph` |

## Emergency Keywords

System **instantly detects** these keywords:
- Cardiac: "chest pain", "heart attack"
- Respiratory: "can't breathe", "choking"
- Neurological: "stroke", "seizure", "unconscious"
- Trauma: "severe bleeding", "major injury"
- Other: "overdose", "suicide", "anaphylaxis"

When detected → Immediate emergency response with warning!

## Test the System

```bash
# Run comprehensive test suite
python examples/test_supervisor.py
```

This tests:
- ✅ Symptom checks
- ✅ Emergency detection
- ✅ All intent types
- ✅ Session continuity
- ✅ Metadata accuracy

## Current Status

✅ **Working:**
- Risk & intent classification
- Emergency detection & warnings
- Session management
- Comprehensive metadata
- Mock graph responses

🔄 **Using Mocks:**
- Graph responses are predefined
- Actual graph workflows coming next

## Files Modified/Created

**Core Implementation:**
- `app/supervisor/constants.py` ← Intent/risk definitions
- `app/supervisor/risk_classifier.py` ← Risk assessment
- `app/supervisor/intent_classifier.py` ← Intent detection
- `app/supervisor/router.py` ← Graph routing
- `app/supervisor/supervisor_graph.py` ← Main orchestrator
- `app/api/chat.py` ← API integration + warning

**Documentation:**
- `docs/supervisor-integration.md` ← Detailed guide
- `SUPERVISOR_README.md` ← Implementation summary
- `examples/test_supervisor.py` ← Test suite

## Next Steps

1. **Implement Graphs** (Epic 3-6)
   - Replace mock responses with actual graph workflows
   - Each graph handles specific medical flows

2. **Add RAG** (Epic 7)
   - Medical knowledge retrieval
   - Ayurvedic text integration

3. **Safety Layer** (Epic 8)
   - Hallucination detection
   - Compliance checks

## Need Help?

Check these docs:
- **Full guide**: `docs/supervisor-integration.md`
- **Architecture**: `docs/architecture.md`
- **Tasks**: `docs/PROJECT_TASKS.md`

---

**Ready to go!** 🚀 The supervisor system is fully integrated and working with mock responses.
