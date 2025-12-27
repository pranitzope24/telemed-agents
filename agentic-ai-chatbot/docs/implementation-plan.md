# Implementation Plan

## Project Phases Overview

This document outlines a step-by-step approach to build the Agentic AI Chatbot system from foundation to production deployment.

---

## Phase 1: Foundation Setup (Week 1-2)

### Goal: Get basic infrastructure running

**Tasks:**
1. **Environment Setup**
   - Install Python 3.11+, Docker, Redis, PostgreSQL
   - Set up virtual environment
   - Install core dependencies: FastAPI, LangChain, LangGraph, OpenAI SDK
   - Configure `.env` with API keys

2. **Core Configuration**
   - Implement `app/config/settings.py` (load from .env)
   - Implement `app/config/llm.py` (OpenAI client setup)
   - Implement `app/utils/logger.py` (structured logging)
   - Add `__init__.py` to all packages

3. **State Management Foundation**
   - Implement `app/state/base_state.py` (BaseState dataclass)
   - Implement `app/state/graph_state.py` (SessionState model)
   - Implement `app/memory/short_term.py` (Redis client wrapper)
   - Write simple set/get/delete methods

4. **Basic API**
   - Implement `app/api/health.py` (health check endpoint)
   - Implement `app/api/chat.py` (skeleton: accept message, return echo)
   - Run FastAPI server locally
   - Test with curl/Postman

**Deliverable:** Working FastAPI server that echoes messages and stores session in Redis

**Validation:** 
```bash
curl -X POST http://localhost:8000/chat -d '{"message": "hello", "session_id": "test"}'
```

---

## Phase 2: Supervisor & Routing (Week 3)

### Goal: Build the orchestration layer

**Tasks:**
1. **Intent Classification**
   - Implement `app/supervisor/intent_classifier.py`
   - Use simple LLM prompt to classify: symptom, dosha, follow-up, emergency
   - Write unit tests with sample inputs

2. **Risk Classification**
   - Implement `app/supervisor/risk_classifier.py`
   - Classify: low, medium, high, emergency
   - Add emergency keyword detection (chest pain, bleeding, etc.)

3. **Router Logic**
   - Implement `app/supervisor/router.py`
   - Map (intent, risk) → graph_name
   - Add handoff logic for emergency cases

4. **Supervisor Graph**
   - Implement `app/supervisor/supervisor_graph.py`
   - Create simple LangGraph: classify → route → invoke graph
   - Return mock response for now

**Deliverable:** Supervisor that routes messages to correct graph (mocked responses)

**Validation:** Test messages trigger correct graph selection

---

## Phase 3: First Working Graph - Symptoms (Week 4-5)

### Goal: Complete end-to-end flow for one graph

**Tasks:**
1. **Symptoms State**
   - Implement `app/graphs/symptoms_graph/state.py` (SymptomsState dataclass)
   - Define fields: raw_complaint, structured_symptoms, triage_outcome, etc.

2. **Symptom Triage Agent**
   - Implement `app/agents/symptom_triage_agent.py`
   - Use LLM to extract symptoms and assess urgency
   - Return structured JSON

3. **Symptoms Graph Nodes**
   - Implement nodes in `app/graphs/symptoms_graph/nodes.py`:
     - `normalize_input_node`
     - `extract_symptoms_node`
     - `triage_node`
     - `specialty_recommendation_node`
   
4. **Symptoms Graph Orchestration**
   - Implement `app/graphs/symptoms_graph/graph.py`
   - Connect nodes in LangGraph
   - Handle conditional routing (emergency → exit early)

5. **Integration**
   - Connect supervisor to symptoms_graph
   - Update `api/chat.py` to invoke supervisor
   - Store state in Redis between turns

**Deliverable:** Working symptom collection → triage → specialty recommendation flow

**Validation:** Multi-turn conversation collects symptoms and provides recommendations

---

## Phase 4: Safety & Emergency (Week 6)

### Goal: Add critical safety guardrails

**Tasks:**
1. **Emergency Detection**
   - Implement `app/safety/emergency_detector.py`
   - Keyword matching + LLM-based severity check
   - Return emergency classification

2. **Emergency Graph**
   - Implement `app/graphs/emergency_graph/graph.py`
   - Nodes: classify → immediate_guidance → escalation → audit
   - Provide first-aid instructions, escalation prompts

3. **Safety Agent**
   - Implement `app/safety/safety_agent.py`
   - Check every LLM output for harmful content
   - Add medical disclaimer to responses

4. **Compliance Checker**
   - Implement `app/safety/compliance_checker.py`
   - Validate prescriptions, medical advice
   - Block non-compliant outputs

5. **Integration**
   - Add safety checks to all graph nodes
   - Route high-risk cases to emergency_graph
   - Log all safety events

**Deliverable:** System detects emergencies and provides appropriate guidance

**Validation:** Emergency keywords trigger immediate response and escalation

---

## Phase 5: Additional Graphs (Week 7-9)

### Goal: Implement remaining domain graphs

**Week 7: Dosha Graph**
1. Implement `app/agents/dosha_inference_agent.py`
2. Implement `app/agents/questionnaire_agent.py`
3. Build questionnaire flow nodes
4. Add dosha calculation logic
5. Test multi-turn questionnaire

**Week 8: Doctor Matching Graph**
1. Implement `app/tools/doctor_service.py` (mock API initially)
2. Implement `app/tools/booking_service.py`
3. Build doctor search, ranking, selection nodes
4. Add booking confirmation flow
5. Test end-to-end booking

**Week 9: Prescription Graph**
1. Implement `app/agents/prescription_draft_agent.py`
2. Implement `app/agents/drug_interaction_agent.py`
3. Build prescription draft → review → approval flow
4. Add PDF generation placeholder
5. Test doctor review loop

**Deliverable:** All core graphs functional with mock external services

**Validation:** Each graph completes its workflow independently

---

## Phase 6: RAG & Knowledge Base (Week 10-11)

### Goal: Add knowledge grounding

**Tasks:**
1. **Vector Store Setup**
   - Set up pgvector in PostgreSQL (or Pinecone)
   - Implement `app/rag/vector_store.py` (embed, search)

2. **Ayurveda Knowledge**
   - Collect Ayurveda texts/PDFs
   - Implement `app/rag/ayurveda/loader.py` (chunk documents)
   - Implement `app/rag/ayurveda/retriever.py` (semantic search)
   - Index documents in vector store

3. **Medical Knowledge**
   - Add medical reference materials
   - Implement `app/rag/medical/loader.py` and `retriever.py`
   - Index medical docs

4. **Safety Guidelines**
   - Add `app/rag/safety/rules.yaml` (contraindications, dosage limits)
   - Implement safety rule retrieval

5. **Integration**
   - Add RAG retrieval to dosha_graph, prescription_graph
   - Use retrieved context in LLM prompts
   - Test improved accuracy

**Deliverable:** Graphs use RAG for grounded, accurate responses

**Validation:** Responses cite Ayurvedic principles and medical references

---

## Phase 7: Long-term Memory & Progress (Week 12-13)

### Goal: Persistent user history and monitoring

**Tasks:**
1. **Database Schema**
   - Design PostgreSQL schema: users, sessions, prescriptions, progress_logs
   - Create migration scripts
   - Implement `app/tools/user_service.py` (CRUD operations)

2. **Long-term Memory**
   - Implement `app/memory/long_term.py` (store/retrieve from DB)
   - Implement `app/memory/episodic.py` (conversation summaries)
   - Store completed sessions in DB

3. **Progress Graph**
   - Implement `app/agents/trend_analysis_agent.py`
   - Implement `app/agents/followup_agent.py`
   - Build progress monitoring nodes
   - Add daily log collection

4. **Notifications**
   - Implement `app/tools/notification_service.py`
   - Send reminders, alerts, confirmations
   - Integrate with progress_graph

**Deliverable:** System tracks user history and monitors progress over time

**Validation:** Follow-up conversations reference past sessions; trends detected

---

## Phase 8: Testing & Quality (Week 14-15)

### Goal: Comprehensive testing and refinement

**Tasks:**
1. **Unit Tests**
   - Write tests for all agents (`tests/test_agents/`)
   - Write tests for all graph nodes
   - Aim for >80% coverage

2. **Integration Tests**
   - Implement `tests/test_symptoms_graph.py` (end-to-end)
   - Implement `tests/test_prescription_flow.py`
   - Implement `tests/test_emergency_flow.py`
   - Test multi-graph handoffs

3. **Safety Tests**
   - Test emergency detection (edge cases)
   - Test hallucination prevention
   - Test compliance validation
   - Red-team with adversarial inputs

4. **Performance Tests**
   - Load test API endpoints
   - Optimize slow LLM calls (caching, streaming)
   - Monitor Redis/DB performance

5. **User Testing**
   - Run manual test scenarios
   - Collect feedback on conversation flow
   - Refine prompts based on results

**Deliverable:** Robust, well-tested system ready for deployment

**Validation:** All tests pass; system handles edge cases gracefully

---

## Phase 9: Production Prep (Week 16-17)

### Goal: Deployment readiness

**Tasks:**
1. **Containerization**
   - Create Dockerfile for app
   - Create docker-compose.yml (app, Redis, PostgreSQL, pgvector)
   - Test local Docker deployment

2. **Configuration Management**
   - Externalize all secrets to environment variables
   - Add feature flags for gradual rollout
   - Set up different configs (dev, staging, prod)

3. **Monitoring & Logging**
   - Add structured logging to all components
   - Set up log aggregation (optional: ELK stack)
   - Add metrics (Prometheus) for API latency, graph execution time
   - Set up alerts for errors, emergencies

4. **Documentation**
   - Complete API documentation (OpenAPI/Swagger)
   - Write deployment guide
   - Write operator runbook
   - Update `README.md` with setup instructions

5. **Security Hardening**
   - Add authentication (API keys or OAuth)
   - Enable HTTPS
   - Sanitize all user inputs
   - Run security audit

**Deliverable:** Production-ready containerized application

**Validation:** Deploy to staging environment; smoke tests pass

---

## Phase 10: Deployment & Monitoring (Week 18+)

### Goal: Launch and iterate

**Tasks:**
1. **Initial Deployment**
   - Deploy to production (cloud VM, Kubernetes, or platform)
   - Set up backup and restore procedures
   - Configure auto-scaling (if needed)

2. **Pilot Launch**
   - Onboard limited users (alpha/beta)
   - Monitor for bugs and performance issues
   - Collect user feedback

3. **Iteration**
   - Fix bugs from production
   - Improve prompts based on real conversations
   - Add new features based on feedback

4. **Scaling**
   - Optimize bottlenecks
   - Add caching layers
   - Scale infrastructure as needed

5. **Compliance & Audit**
   - Regular safety audits
   - Review logged emergency cases
   - Ensure HIPAA/GDPR compliance (if applicable)

**Deliverable:** Live production system serving real users

**Validation:** System handles production traffic; users achieve their goals

---

## Simplified Timeline Summary

| Phase | Duration | Focus | Key Milestone |
|-------|----------|-------|---------------|
| 1 | Week 1-2 | Foundation | FastAPI + Redis working |
| 2 | Week 3 | Supervisor | Intent/risk routing |
| 3 | Week 4-5 | First Graph | Symptoms graph complete |
| 4 | Week 6 | Safety | Emergency handling |
| 5 | Week 7-9 | More Graphs | All graphs functional |
| 6 | Week 10-11 | RAG | Knowledge grounding |
| 7 | Week 12-13 | Memory | Progress tracking |
| 8 | Week 14-15 | Testing | >80% test coverage |
| 9 | Week 16-17 | Production Prep | Dockerized, monitored |
| 10 | Week 18+ | Launch | Live production |

**Total: ~4-5 months to production-ready system**

---

## Development Best Practices

1. **Start Simple**: Get one flow working end-to-end before adding complexity
2. **Test Early**: Write tests as you build, not after
3. **Mock External Services**: Use mocks until ready to integrate real APIs
4. **Version Control**: Commit frequently with clear messages
5. **Code Reviews**: Review your own code before committing
6. **Documentation**: Update docs as you build features
7. **Iterative**: Don't try to perfect everything; iterate based on testing
8. **Safety First**: Never skip safety checks, even in development

---

## Risk Mitigation

**Common Pitfalls:**
- **Over-engineering early**: Start with simple implementations, optimize later
- **LLM reliability**: Always have fallbacks for LLM failures
- **State management bugs**: Test pause/resume flows thoroughly
- **Security gaps**: Audit safety layer regularly
- **Scope creep**: Stick to phases; add "nice-to-haves" post-MVP

**Mitigation Strategies:**
- Keep each phase focused on specific deliverables
- Use mocks and stubs to unblock development
- Build safety checks into every component from day one
- Regular testing and feedback loops
- Clear separation of concerns (graphs, agents, tools)

---

## Success Metrics

**Phase Completion Criteria:**
- ✅ All code for the phase committed and tested
- ✅ Integration tests pass
- ✅ Documentation updated
- ✅ Demo/walkthrough completed
- ✅ Ready to move to next phase

**Production Readiness:**
- ✅ All 6 graphs operational
- ✅ Safety checks in place
- ✅ >80% test coverage
- ✅ <2s API response time (p95)
- ✅ Zero critical security issues
- ✅ Monitoring and alerts configured
- ✅ Deployment automation complete

---

## Next Steps

1. **Start with Phase 1**: Set up environment, install dependencies
2. **Create a development branch**: `git checkout -b develop`
3. **Track progress**: Use GitHub Issues or project board
4. **Daily commits**: Commit working code at end of each day
5. **Weekly reviews**: Review progress against plan each week

**First Command to Run:**
```bash
cd agentic-ai-chatbot
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install fastapi uvicorn redis python-dotenv langchain langgraph openai
```

Good luck! 🚀
