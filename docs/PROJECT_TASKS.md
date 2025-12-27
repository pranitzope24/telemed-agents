# Project Tasks & User Stories

This document contains all user stories and tasks for the Agentic AI Chatbot project, organized for GitHub Projects. Tasks are labeled with dependencies and parallelization opportunities for two-person team.

---

## Legend

- 🔴 **Blocker**: Must be completed before dependent tasks
- 🟡 **Can Parallelize**: Can be done simultaneously by different team members
- 🟢 **Independent**: No dependencies, start anytime
- 👤 **Person A / Person B**: Suggested assignment for parallel work

---

## Epic 1: Foundation & Infrastructure Setup

### Sprint 1: Environment & Core Setup (Week 1-2)

#### Story 1.1: Project Environment Setup
**As a developer, I want a working development environment so I can start building features.**

**Tasks:**
- [ done ] **TASK-001** 🔴 Set up Python 3.11+ virtual environment (Person A)
  - Create venv
  - Document setup in README
  - Estimate: 0.5h
  
- [ done ] **TASK-002** 🔴 Install and configure Redis locally (Person B)
  - Install Redis via Docker or native
  - Test connection
  - Document in README
  - Estimate: 1h
  
- [ done ] **TASK-003** 🔴 Install and configure PostgreSQL (Person B)
  - Install Postgres via Docker or native
  - Create database
  - Document in README
  - Estimate: 1h

  docker-compose.yaml setup - DONE
  
- [ done ] **TASK-004** 🟡 Create requirements.txt with core dependencies (Person A)
  - Add FastAPI, LangChain, LangGraph, Redis, SQLAlchemy
  - Add dev dependencies (pytest, black, ruff)
  - Estimate: 0.5h
  
- [ ] **TASK-005** 🟡 Create .env.example and .gitignore (Person A)
  - Define all environment variables
  - Add .gitignore for Python projects
  - Estimate: 0.5h
  
- [ ] **TASK-006** Set up Git hooks for code quality (Person B)
  - Pre-commit hooks (black, ruff)
  - Estimate: 1h

**Acceptance Criteria:**
- ✅ Virtual environment activates successfully
- ✅ Redis and Postgres running and accessible
- ✅ All dependencies install without errors
- ✅ .env file configured with valid credentials

---

#### Story 1.2: Core Configuration System
**As a developer, I want centralized configuration management so settings are consistent across the app.**

**Tasks:**
- [ ] **TASK-007** 🔴 Implement app/config/settings.py (Person A)
  - Pydantic Settings class
  - Load from .env
  - Validation
  - Estimate: 2h
  
- [ ] **TASK-008** 🟡 Implement app/config/llm.py (Person A)
  - LLM client factory (OpenAI, Anthropic)
  - Temperature/model configuration
  - Estimate: 1.5h
  
- [ ] **TASK-009** 🟡 Implement app/config/embeddings.py (Person B)
  - Embedding model config
  - Estimate: 1h
  
- [ ] **TASK-010** 🟡 Implement app/config/models.py (Person B)
  - Model registry/versioning
  - Estimate: 1h
  
- [ ] **TASK-011** 🟡 Implement app/config/feature_flags.py (Person B)
  - Feature toggle system
  - Estimate: 1h
  
- [ ] **TASK-012** Write unit tests for config module (Person A)
  - Test settings loading
  - Test validation
  - Estimate: 1.5h

**Acceptance Criteria:**
- ✅ Settings load correctly from .env
- ✅ LLM clients initialize successfully
- ✅ All tests pass
- ✅ Invalid config throws meaningful errors

---

#### Story 1.3: Utilities & Logging
**As a developer, I want common utilities and structured logging for debugging.**

**Tasks:**
- [ ] **TASK-013** 🟡 Implement app/utils/logger.py (Person A)
  - Structured logging setup
  - Log levels from config
  - Estimate: 1.5h
  
- [ ] **TASK-014** 🟡 Implement app/utils/ids.py (Person B)
  - UUID generation helpers
  - Estimate: 0.5h
  
- [ ] **TASK-015** 🟡 Implement app/utils/time.py (Person B)
  - Timestamp utilities
  - Estimate: 0.5h
  
- [ ] **TASK-016** 🟡 Implement app/utils/retry.py (Person A)
  - Retry decorator with exponential backoff
  - Estimate: 1.5h
  
- [ ] **TASK-017** Write tests for utils module (Both)
  - Test each utility
  - Estimate: 1h

**Acceptance Criteria:**
- ✅ Logs output in structured format
- ✅ Retry logic works correctly
- ✅ All utility tests pass

---

#### Story 1.4: State Management Foundation
**As a developer, I want state management infrastructure for session handling.**

**Tasks:**
- [ ] **TASK-018** 🔴 Implement app/state/base_state.py (Person A)
  - BaseState dataclass
  - to_dict/from_dict methods
  - JSON serialization
  - Estimate: 2h
  
- [ ] **TASK-019** Implement app/state/graph_state.py (Person A)
  - SessionState model
  - Message model
  - Estimate: 2h
  
- [ ] **TASK-020** 🟡 Implement app/state/user_state.py (Person B)
  - User profile state
  - Estimate: 1h
  
- [ ] **TASK-021** 🟡 Implement app/state/medical_state.py (Person B)
  - Medical context state
  - Estimate: 1h
  
- [ ] **TASK-022** 🟡 Implement app/state/conversation_state.py (Person B)
  - Conversation flow state
  - Estimate: 1h
  
- [ ] **TASK-023** Write tests for state models (Both)
  - Test serialization/deserialization
  - Estimate: 1.5h

**Acceptance Criteria:**
- ✅ State classes serialize to/from JSON
- ✅ Type validation works
- ✅ All tests pass

---

#### Story 1.5: Memory Layer (Redis)
**As a developer, I want short-term memory storage for fast session access.**

**Tasks:**
- [ ] **TASK-024** 🔴 Implement app/memory/short_term.py (Person A)
  - Redis client wrapper
  - set/get/delete methods
  - TTL support
  - Error handling
  - Estimate: 3h
  
- [ ] **TASK-025** 🟡 Implement app/memory/session_memory.py (Person B)
  - Session-specific memory helpers
  - Recent turns management
  - Estimate: 2h
  
- [ ] **TASK-026** Write Redis integration tests (Person A)
  - Test CRUD operations
  - Test TTL
  - Estimate: 1.5h

**Acceptance Criteria:**
- ✅ Can set/get data from Redis
- ✅ TTL expires correctly
- ✅ Graceful error handling
- ✅ Tests pass

---

#### Story 1.6: Basic API Endpoints
**As a user, I want to interact with the chatbot via HTTP API.**

**Tasks:**
- [ ] **TASK-027** 🔴 Implement app/main.py (FastAPI app) (Person A)
  - FastAPI app initialization
  - CORS middleware
  - Router registration
  - Estimate: 2h
  
- [ ] **TASK-028** 🟡 Implement app/api/health.py (Person B)
  - Health check endpoint
  - Redis/DB connectivity check
  - Estimate: 1h
  
- [ ] **TASK-029** 🔴 Implement app/api/chat.py (skeleton) (Person A)
  - POST /chat endpoint
  - Session ID handling
  - State loading/saving
  - Echo response (temporary)
  - Estimate: 3h
  
- [ ] **TASK-030** 🟡 Implement app/api/session.py (Person B)
  - POST /session (create)
  - GET /session/{id} (retrieve)
  - DELETE /session/{id} (terminate)
  - Estimate: 2h
  
- [ ] **TASK-031** Write API integration tests (Both)
  - Test all endpoints
  - Estimate: 2h

**Acceptance Criteria:**
- ✅ Server starts without errors
- ✅ /health returns 200
- ✅ /chat accepts messages and returns responses
- ✅ Session state persists in Redis
- ✅ API tests pass

---

## Epic 2: Supervisor & Routing System

### Sprint 2: Intent & Risk Classification (Week 3)

#### Story 2.1: Intent Classification
**As the system, I want to classify user intent so I can route to the correct graph.**

**Tasks:**
- [ ] **TASK-032** 🔴 Implement app/supervisor/constants.py (Person A)
  - Define intent types
  - Define risk levels
  - Define graph names
  - Estimate: 0.5h
  
- [ ] **TASK-033** 🔴 Implement app/supervisor/intent_classifier.py (Person A)
  - LLM-based intent classification
  - Prompt engineering
  - Fallback logic
  - Estimate: 3h
  
- [ ] **TASK-034** Write intent classifier tests (Person A)
  - Test all intent categories
  - Test edge cases
  - Estimate: 2h

**Acceptance Criteria:**
- ✅ Correctly classifies symptom/dosha/doctor/emergency intents
- ✅ Handles ambiguous inputs gracefully
- ✅ Tests achieve >90% accuracy on test cases

---

#### Story 2.2: Risk Classification
**As the system, I want to assess medical risk so I can prioritize emergencies.**

**Tasks:**
- [ ] **TASK-035** 🟡 Implement app/supervisor/risk_classifier.py (Person B)
  - Emergency keyword detection
  - LLM-based risk assessment
  - Multi-tier risk (low/med/high/emergency)
  - Estimate: 3h
  
- [ ] **TASK-036** Write risk classifier tests (Person B)
  - Test emergency keywords
  - Test risk levels
  - Test false positives/negatives
  - Estimate: 2h

**Acceptance Criteria:**
- ✅ Detects emergency keywords immediately
- ✅ Correctly classifies risk levels
- ✅ No false negatives for emergencies
- ✅ Tests pass

---

#### Story 2.3: Routing Logic
**As the system, I want routing logic to select the appropriate graph.**

**Tasks:**
- [ ] **TASK-037** 🔴 Implement app/supervisor/router.py (Person A)
  - Intent + risk → graph mapping
  - Emergency priority routing
  - Handoff logic
  - Estimate: 2h
  
- [ ] **TASK-038** Write router tests (Person A)
  - Test all routing combinations
  - Test emergency priority
  - Estimate: 1.5h

**Acceptance Criteria:**
- ✅ Emergency always routes to emergency_graph
- ✅ Intent correctly maps to graphs
- ✅ Tests cover all combinations

---

#### Story 2.4: Supervisor Orchestration
**As the system, I want a supervisor to orchestrate classification and routing.**

**Tasks:**
- [ ] **TASK-039** 🔴 Implement app/supervisor/supervisor_graph.py (Person B)
  - Classify → route → invoke graph
  - Resume vs new conversation logic
  - State updates
  - Estimate: 4h
  
- [ ] **TASK-040** Integrate supervisor with chat API (Person A)
  - Replace echo logic in chat.py
  - Call supervisor
  - Handle routing results
  - Estimate: 2h
  
- [ ] **TASK-041** Write supervisor integration tests (Both)
  - End-to-end classification → routing
  - Estimate: 2h

**Acceptance Criteria:**
- ✅ Supervisor classifies and routes correctly
- ✅ Chat API uses supervisor
- ✅ State updates properly
- ✅ Tests pass

---

## Epic 3: First Working Graph (Symptoms)

### Sprint 3: Symptoms Graph (Week 4-5)

#### Story 3.1: Symptom Triage Agent
**As the system, I want to analyze symptoms and determine urgency.**

**Tasks:**
- [ ] **TASK-042** 🔴 Implement app/agents/symptom_triage_agent.py (Person A)
  - Symptom extraction (structured)
  - Triage logic (needs_doctor/self_care/emergency)
  - Specialty recommendation
  - Estimate: 4h
  
- [ ] **TASK-043** Write symptom triage tests (Person A)
  - Test extraction accuracy
  - Test triage decisions
  - Estimate: 2h

**Acceptance Criteria:**
- ✅ Extracts symptoms with duration/severity
- ✅ Correctly triages urgency
- ✅ Suggests appropriate specialties
- ✅ Tests pass

---

#### Story 3.2: Symptoms Graph State & Nodes
**As the system, I want a symptoms graph to process symptom inquiries.**

**Tasks:**
- [ ] **TASK-044** 🟡 Implement app/graphs/symptoms_graph/state.py (Person B)
  - SymptomsState dataclass
  - SymptomEntry model
  - Estimate: 1.5h
  
- [ ] **TASK-045** 🟡 Implement app/graphs/symptoms_graph/prompts.py (Person B)
  - Prompts for triage
  - Clarification prompts
  - Estimate: 1h
  
- [ ] **TASK-046** 🔴 Implement app/graphs/symptoms_graph/nodes.py (Person A)
  - normalize_input_node
  - triage_node
  - clarification_node
  - specialty_recommendation_node
  - Estimate: 4h
  
- [ ] **TASK-047** Write node unit tests (Person A)
  - Test each node independently
  - Estimate: 2h

**Acceptance Criteria:**
- ✅ Each node processes state correctly
- ✅ State transitions work
- ✅ Tests pass

---

#### Story 3.3: Symptoms Graph Orchestration
**As the system, I want a LangGraph to orchestrate symptom processing.**

**Tasks:**
- [ ] **TASK-048** 🔴 Implement app/graphs/symptoms_graph/graph.py (Person B)
  - Create LangGraph workflow
  - Node connections
  - Conditional edges (emergency/clarify)
  - Estimate: 4h
  
- [ ] **TASK-049** Integrate symptoms graph with supervisor (Person A)
  - Call from supervisor
  - Handle handoffs
  - Estimate: 2h
  
- [ ] **TASK-050** Write symptoms graph integration tests (Both)
  - End-to-end symptom flow
  - Test emergency handoff
  - Test clarification loop
  - Estimate: 3h

**Acceptance Criteria:**
- ✅ Graph processes symptoms end-to-end
- ✅ Emergency cases handoff correctly
- ✅ Clarification loop works
- ✅ Integration tests pass

---

## Epic 4: Safety & Emergency Handling

### Sprint 4: Safety Layer (Week 6)

#### Story 4.1: Emergency Detection & Response
**As the system, I want to detect and handle medical emergencies immediately.**

**Tasks:**
- [ ] **TASK-051** 🔴 Implement app/safety/emergency_detector.py (Person A)
  - Keyword detection
  - LLM-based severity check
  - Real-time monitoring
  - Estimate: 3h
  
- [ ] **TASK-052** 🔴 Implement app/agents/emergency_response_agent.py (Person A)
  - Emergency classification
  - First-aid guidance
  - Escalation logic
  - Estimate: 3h
  
- [ ] **TASK-053** Write emergency detection tests (Person A)
  - Test keyword triggers
  - Test false positives
  - Estimate: 2h

**Acceptance Criteria:**
- ✅ Detects all emergency keywords
- ✅ Provides appropriate guidance
- ✅ No false negatives for critical cases

---

#### Story 4.2: Emergency Graph
**As a user, I want immediate help when experiencing a medical emergency.**

**Tasks:**
- [ ] **TASK-054** 🟡 Implement app/graphs/emergency_graph/state.py (Person B)
  - EmergencyState model
  - Estimate: 1h
  
- [ ] **TASK-055** 🟡 Implement app/graphs/emergency_graph/prompts.py (Person B)
  - Emergency prompts
  - Estimate: 1h
  
- [ ] **TASK-056** 🔴 Implement app/graphs/emergency_graph/nodes.py (Person A)
  - classify_node
  - immediate_guidance_node
  - escalation_node
  - audit_log_node
  - Estimate: 4h
  
- [ ] **TASK-057** 🔴 Implement app/graphs/emergency_graph/graph.py (Person B)
  - LangGraph workflow
  - Priority execution
  - Estimate: 3h
  
- [ ] **TASK-058** Write emergency graph tests (Both)
  - Test emergency flows
  - Test escalation
  - Estimate: 2h

**Acceptance Criteria:**
- ✅ Emergency graph executes immediately
- ✅ Provides life-saving guidance
- ✅ Logs all actions
- ✅ Tests pass

---

#### Story 4.3: Safety Guardrails
**As the system, I want safety checks on all medical advice.**

**Tasks:**
- [ ] **TASK-059** 🟡 Implement app/safety/safety_agent.py (Person A)
  - Overall safety orchestration
  - Wraps LLM calls
  - Estimate: 3h
  
- [ ] **TASK-060** 🟡 Implement app/safety/compliance_checker.py (Person B)
  - Validate prescriptions
  - Check medical advice
  - Estimate: 3h
  
- [ ] **TASK-061** 🟡 Implement app/safety/hallucination_detector.py (Person A)
  - Detect unsupported claims
  - Cross-reference with knowledge base
  - Estimate: 3h
  
- [ ] **TASK-062** 🟡 Implement app/safety/medical_disclaimer.py (Person B)
  - Add disclaimers to responses
  - Estimate: 1h
  
- [ ] **TASK-063** Integrate safety checks into graphs (Both)
  - Add to all graph nodes
  - Estimate: 2h
  
- [ ] **TASK-064** Write safety tests (Both)
  - Test all safety checks
  - Red team testing
  - Estimate: 3h

**Acceptance Criteria:**
- ✅ All medical advice includes disclaimers
- ✅ Unsafe content blocked
- ✅ Hallucinations detected
- ✅ Tests pass

---

## Epic 5: Additional Graphs

### Sprint 5: Dosha Graph (Week 7)

#### Story 5.1: Ayurvedic Questionnaire
**As a user, I want to complete a questionnaire to learn my Ayurvedic dosha.**

**Tasks:**
- [ ] **TASK-065** 🔴 Implement app/agents/questionnaire_agent.py (Person A)
  - Dynamic questionnaire logic
  - Question selection
  - Answer validation
  - Estimate: 3h
  
- [ ] **TASK-066** 🔴 Implement app/agents/dosha_inference_agent.py (Person A)
  - Dosha calculation algorithm
  - Confidence scoring
  - Estimate: 4h
  
- [ ] **TASK-067** 🟡 Implement app/graphs/dosha_graph/state.py (Person B)
  - DoshaState model
  - Estimate: 1h
  
- [ ] **TASK-068** 🟡 Implement app/graphs/dosha_graph/prompts.py (Person B)
  - Questionnaire prompts
  - Estimate: 2h
  
- [ ] **TASK-069** 🔴 Implement app/graphs/dosha_graph/nodes.py (Person A)
  - questionnaire nodes
  - calculation node
  - confidence check node
  - Estimate: 4h
  
- [ ] **TASK-070** 🔴 Implement app/graphs/dosha_graph/graph.py (Person B)
  - LangGraph with questionnaire loop
  - Estimate: 3h
  
- [ ] **TASK-071** Write dosha graph tests (Both)
  - Test questionnaire flow
  - Test calculation accuracy
  - Estimate: 2h

**Acceptance Criteria:**
- ✅ Questionnaire completes successfully
- ✅ Dosha calculated accurately
- ✅ Confidence check works
- ✅ Tests pass

---

### Sprint 6: Doctor Matching Graph (Week 8)

#### Story 6.1: Doctor Search & Booking
**As a user, I want to find and book an appropriate doctor.**

**Tasks:**
- [ ] **TASK-072** 🟡 Implement app/tools/doctor_service.py (Person A)
  - Doctor search API (mocked initially)
  - Filtering by specialty/location
  - Estimate: 3h
  
- [ ] **TASK-073** 🟡 Implement app/tools/booking_service.py (Person B)
  - Booking API (mocked initially)
  - Availability check
  - Estimate: 3h
  
- [ ] **TASK-074** 🟡 Implement app/graphs/doctor_matching_graph/state.py (Person A)
  - DoctorMatchState model
  - Estimate: 1h
  
- [ ] **TASK-075** 🟡 Implement app/graphs/doctor_matching_graph/prompts.py (Person B)
  - Search prompts
  - Estimate: 1h
  
- [ ] **TASK-076** 🔴 Implement app/graphs/doctor_matching_graph/nodes.py (Person A)
  - search_node
  - ranking_node
  - selection_node
  - booking_node
  - Estimate: 4h
  
- [ ] **TASK-077** 🔴 Implement app/graphs/doctor_matching_graph/graph.py (Person B)
  - LangGraph workflow
  - Estimate: 3h
  
- [ ] **TASK-078** Write doctor matching tests (Both)
  - Test search/ranking
  - Test booking flow
  - Estimate: 2h

**Acceptance Criteria:**
- ✅ Finds relevant doctors
- ✅ Booking confirmation works
- ✅ Tests pass

---

### Sprint 7: Prescription Graph (Week 9)

#### Story 7.1: Prescription Drafting & Approval
**As a user, I want a safe prescription reviewed by a doctor.**

**Tasks:**
- [ ] **TASK-079** 🔴 Implement app/agents/prescription_draft_agent.py (Person A)
  - Prescription generation
  - Dosage recommendations
  - Estimate: 4h
  
- [ ] **TASK-080** 🔴 Implement app/agents/drug_interaction_agent.py (Person A)
  - Drug interaction checking
  - Contraindication detection
  - Estimate: 4h
  
- [ ] **TASK-081** 🟡 Implement app/tools/prescription_service.py (Person B)
  - Prescription storage
  - PDF generation (placeholder)
  - Estimate: 3h
  
- [ ] **TASK-082** 🟡 Implement app/graphs/prescription_graph/state.py (Person B)
  - PrescriptionState model
  - Estimate: 1h
  
- [ ] **TASK-083** 🟡 Implement app/graphs/prescription_graph/prompts.py (Person B)
  - Prescription prompts
  - Estimate: 1h
  
- [ ] **TASK-084** 🔴 Implement app/graphs/prescription_graph/nodes.py (Person A)
  - draft_node
  - interaction_check_node
  - doctor_review_node
  - pdf_generation_node
  - Estimate: 5h
  
- [ ] **TASK-085** 🔴 Implement app/graphs/prescription_graph/graph.py (Person B)
  - LangGraph with approval loop
  - Estimate: 3h
  
- [ ] **TASK-086** Write prescription graph tests (Both)
  - Test draft generation
  - Test interaction checks
  - Test approval flow
  - Estimate: 3h

**Acceptance Criteria:**
- ✅ Prescription drafted correctly
- ✅ Interactions detected
- ✅ Doctor approval loop works
- ✅ Tests pass

---

## Epic 6: RAG & Knowledge Base

### Sprint 8: Vector Store & RAG (Week 10-11)

#### Story 6.1: Vector Store Setup
**As the system, I want a vector database for knowledge retrieval.**

**Tasks:**
- [ ] **TASK-087** 🔴 Set up pgvector extension in PostgreSQL (Person A)
  - Install pgvector
  - Create vector tables
  - Estimate: 2h
  
- [ ] **TASK-088** 🔴 Implement app/rag/vector_store.py (Person A)
  - Embedding generation
  - Vector search
  - CRUD operations
  - Estimate: 4h
  
- [ ] **TASK-089** Write vector store tests (Person A)
  - Test embeddings
  - Test search
  - Estimate: 2h

**Acceptance Criteria:**
- ✅ pgvector installed and working
- ✅ Can embed and search documents
- ✅ Tests pass

---

#### Story 6.2: Ayurveda Knowledge Base
**As the system, I want Ayurvedic knowledge for accurate recommendations.**

**Tasks:**
- [ ] **TASK-090** 🟡 Collect Ayurveda texts/documents (Person B)
  - Research public domain texts
  - Organize documents
  - Estimate: 3h
  
- [ ] **TASK-091** 🔴 Implement app/rag/ayurveda/loader.py (Person A)
  - Document chunking
  - Metadata extraction
  - Estimate: 3h
  
- [ ] **TASK-092** 🔴 Implement app/rag/ayurveda/retriever.py (Person A)
  - Semantic search
  - Re-ranking
  - Estimate: 3h
  
- [ ] **TASK-093** 🟡 Implement app/rag/ayurveda/prompts.py (Person B)
  - RAG prompts
  - Estimate: 1h
  
- [ ] **TASK-094** 🔴 Run script to index Ayurveda docs (Person A)
  - scripts/ingest_ayurveda_docs.py
  - Estimate: 2h
  
- [ ] **TASK-095** Write Ayurveda RAG tests (Person A)
  - Test retrieval accuracy
  - Estimate: 2h

**Acceptance Criteria:**
- ✅ Ayurveda texts indexed
- ✅ Retrieval returns relevant passages
- ✅ Tests pass

---

#### Story 6.3: Medical Knowledge Base
**As the system, I want medical references for evidence-based advice.**

**Tasks:**
- [ ] **TASK-096** 🟡 Collect medical reference materials (Person B)
  - Research medical sources
  - Organize documents
  - Estimate: 3h
  
- [ ] **TASK-097** 🟡 Implement app/rag/medical/loader.py (Person B)
  - Document chunking
  - Estimate: 2h
  
- [ ] **TASK-098** 🟡 Implement app/rag/medical/retriever.py (Person B)
  - Semantic search
  - Estimate: 2h
  
- [ ] **TASK-099** 🔴 Run script to index medical docs (Person B)
  - scripts/build_vector_index.py
  - Estimate: 2h
  
- [ ] **TASK-100** Write medical RAG tests (Person B)
  - Test retrieval
  - Estimate: 2h

**Acceptance Criteria:**
- ✅ Medical docs indexed
- ✅ Retrieval works
- ✅ Tests pass

---

#### Story 6.4: Integrate RAG into Graphs
**As the system, I want graphs to use RAG for grounded responses.**

**Tasks:**
- [ ] **TASK-101** Integrate RAG into dosha_graph (Person A)
  - Use Ayurveda retriever in nodes
  - Estimate: 2h
  
- [ ] **TASK-102** Integrate RAG into prescription_graph (Person B)
  - Use medical retriever in nodes
  - Estimate: 2h
  
- [ ] **TASK-103** Test RAG integration (Both)
  - Verify improved accuracy
  - Estimate: 2h

**Acceptance Criteria:**
- ✅ Graphs use RAG context
- ✅ Responses cite sources
- ✅ Accuracy improved

---

## Epic 7: Long-term Memory & Progress Tracking

### Sprint 9: Database & Memory (Week 12-13)

#### Story 7.1: Database Schema & Models
**As the system, I want persistent storage for user data and history.**

**Tasks:**
- [ ] **TASK-104** 🔴 Design PostgreSQL schema (Person A)
  - Tables: users, sessions, prescriptions, logs
  - Create migration script
  - Estimate: 3h
  
- [ ] **TASK-105** 🔴 Implement app/tools/user_service.py (Person A)
  - User CRUD operations
  - SQLAlchemy models
  - Estimate: 4h
  
- [ ] **TASK-106** 🟡 Implement app/tools/analytics_service.py (Person B)
  - Usage analytics
  - Reporting
  - Estimate: 3h
  
- [ ] **TASK-107** 🟡 Implement app/tools/notification_service.py (Person B)
  - Email/SMS sending (mocked)
  - Estimate: 2h
  
- [ ] **TASK-108** Write database tests (Both)
  - Test CRUD operations
  - Estimate: 2h

**Acceptance Criteria:**
- ✅ Schema created successfully
- ✅ CRUD operations work
- ✅ Tests pass

---

#### Story 7.2: Long-term Memory
**As the system, I want to store and retrieve user history.**

**Tasks:**
- [ ] **TASK-109** 🔴 Implement app/memory/long_term.py (Person A)
  - Store completed sessions in DB
  - Retrieve user history
  - Estimate: 3h
  
- [ ] **TASK-110** 🟡 Implement app/memory/episodic.py (Person B)
  - Conversation summaries
  - Episode retrieval
  - Estimate: 3h
  
- [ ] **TASK-111** Write memory tests (Both)
  - Test storage/retrieval
  - Estimate: 2h

**Acceptance Criteria:**
- ✅ Sessions stored in DB
- ✅ History retrieved correctly
- ✅ Tests pass

---

#### Story 7.3: Progress Tracking Graph
**As a user, I want to track my treatment progress over time.**

**Tasks:**
- [ ] **TASK-112** 🔴 Implement app/agents/trend_analysis_agent.py (Person A)
  - Analyze symptom trends
  - Detect improvement/worsening
  - Estimate: 4h
  
- [ ] **TASK-113** 🔴 Implement app/agents/followup_agent.py (Person A)
  - Generate follow-up recommendations
  - Estimate: 3h
  
- [ ] **TASK-114** 🟡 Implement app/graphs/progress_graph/state.py (Person B)
  - ProgressState model
  - Estimate: 1h
  
- [ ] **TASK-115** 🟡 Implement app/graphs/progress_graph/prompts.py (Person B)
  - Progress prompts
  - Estimate: 1h
  
- [ ] **TASK-116** 🔴 Implement app/graphs/progress_graph/nodes.py (Person A)
  - log_collection_node
  - trend_analysis_node
  - followup_node
  - Estimate: 4h
  
- [ ] **TASK-117** 🔴 Implement app/graphs/progress_graph/graph.py (Person B)
  - LangGraph workflow
  - Estimate: 3h
  
- [ ] **TASK-118** Write progress graph tests (Both)
  - Test trend detection
  - Test follow-ups
  - Estimate: 2h

**Acceptance Criteria:**
- ✅ Trends detected accurately
- ✅ Follow-ups generated
- ✅ Tests pass

---

## Epic 8: Testing & Quality Assurance

### Sprint 10: Comprehensive Testing (Week 14-15)

#### Story 8.1: Unit Tests
**As a developer, I want comprehensive unit tests for all components.**

**Tasks:**
- [ ] **TASK-119** 🟡 Write unit tests for all agents (Person A)
  - tests/test_agents/
  - Estimate: 6h
  
- [ ] **TASK-120** 🟡 Write unit tests for all tools (Person B)
  - tests/test_tools/
  - Estimate: 4h
  
- [ ] **TASK-121** 🟡 Write unit tests for safety module (Person A)
  - tests/test_safety/
  - Estimate: 3h
  
- [ ] **TASK-122** Measure code coverage (Both)
  - Run coverage report
  - Aim for >80%
  - Estimate: 1h

**Acceptance Criteria:**
- ✅ >80% code coverage
- ✅ All unit tests pass

---

#### Story 8.2: Integration Tests
**As a developer, I want integration tests for graph workflows.**

**Tasks:**
- [ ] **TASK-123** Implement tests/test_symptoms_graph.py (Person A)
  - End-to-end symptom flow
  - Estimate: 3h
  
- [ ] **TASK-124** Implement tests/test_dosha_graph.py (Person B)
  - End-to-end dosha flow
  - Estimate: 3h
  
- [ ] **TASK-125** Implement tests/test_prescription_flow.py (Person A)
  - End-to-end prescription flow
  - Estimate: 3h
  
- [ ] **TASK-126** Implement tests/test_emergency_flow.py (Person B)
  - Emergency detection and response
  - Estimate: 2h
  
- [ ] **TASK-127** Implement tests/test_supervisor.py (Person A)
  - Supervisor routing
  - Estimate: 2h

**Acceptance Criteria:**
- ✅ All integration tests pass
- ✅ Graphs work end-to-end

---

#### Story 8.3: Safety & Edge Case Testing
**As a developer, I want to ensure system safety and robustness.**

**Tasks:**
- [ ] **TASK-128** Implement tests/test_safety.py (Person A)
  - Test all safety checks
  - Estimate: 3h
  
- [ ] **TASK-129** Red team testing (Both)
  - Adversarial inputs
  - Jailbreak attempts
  - Edge cases
  - Estimate: 4h
  
- [ ] **TASK-130** Performance testing (Person B)
  - Load test API endpoints
  - Measure latency
  - Estimate: 3h

**Acceptance Criteria:**
- ✅ No safety vulnerabilities
- ✅ Handles edge cases gracefully
- ✅ Meets performance targets (<2s p95)

---

## Epic 9: Production Preparation

### Sprint 11: Deployment Setup (Week 16-17)

#### Story 9.1: Containerization
**As a DevOps engineer, I want containerized deployment.**

**Tasks:**
- [ ] **TASK-131** 🔴 Create Dockerfile (Person A)
  - Multi-stage build
  - Optimize image size
  - Estimate: 3h
  
- [ ] **TASK-132** 🔴 Create docker-compose.yml (Person A)
  - App, Redis, PostgreSQL, pgvector
  - Environment configs
  - Estimate: 2h
  
- [ ] **TASK-133** Test Docker deployment locally (Person A)
  - Build and run containers
  - Verify connectivity
  - Estimate: 2h

**Acceptance Criteria:**
- ✅ Docker builds successfully
- ✅ All services start
- ✅ App accessible via Docker

---

#### Story 9.2: Configuration Management
**As a DevOps engineer, I want environment-specific configs.**

**Tasks:**
- [ ] **TASK-134** 🟡 Create config files for dev/staging/prod (Person B)
  - Separate .env files
  - Document differences
  - Estimate: 2h
  
- [ ] **TASK-135** 🟡 Externalize all secrets (Person B)
  - Move to environment variables
  - Update documentation
  - Estimate: 1h

**Acceptance Criteria:**
- ✅ No secrets in code
- ✅ Environment-specific configs work

---

#### Story 9.3: Monitoring & Logging
**As an operator, I want monitoring and observability.**

**Tasks:**
- [ ] **TASK-136** 🟡 Set up structured logging across app (Person A)
  - Ensure all components log properly
  - Estimate: 2h
  
- [ ] **TASK-137** 🟡 Add Prometheus metrics (optional) (Person B)
  - Request latency
  - Graph execution time
  - Estimate: 3h
  
- [ ] **TASK-138** 🟡 Set up health check monitoring (Person A)
  - Periodic checks
  - Alerting
  - Estimate: 2h

**Acceptance Criteria:**
- ✅ Logs are structured and searchable
- ✅ Metrics collected
- ✅ Alerts configured

---

#### Story 9.4: Documentation
**As a developer, I want complete documentation for deployment and usage.**

**Tasks:**
- [ ] **TASK-139** Update README.md (Person A)
  - Setup instructions
  - Usage examples
  - Estimate: 2h
  
- [ ] **TASK-140** Create deployment guide (Person B)
  - docs/deployment.md
  - Step-by-step deployment
  - Estimate: 2h
  
- [ ] **TASK-141** Create API documentation (Person A)
  - OpenAPI/Swagger
  - Estimate: 2h
  
- [ ] **TASK-142** Create operator runbook (Person B)
  - Troubleshooting guide
  - Estimate: 2h

**Acceptance Criteria:**
- ✅ README complete and accurate
- ✅ Deployment guide tested
- ✅ API docs generated
- ✅ Runbook covers common issues

---

#### Story 9.5: Security Hardening
**As a security engineer, I want the app secured for production.**

**Tasks:**
- [ ] **TASK-143** 🟡 Add authentication to API (Person A)
  - API key or OAuth
  - Estimate: 4h
  
- [ ] **TASK-144** 🟡 Enable HTTPS (Person B)
  - SSL/TLS certificates
  - Estimate: 2h
  
- [ ] **TASK-145** 🟡 Input validation and sanitization (Person A)
  - Validate all user inputs
  - Estimate: 2h
  
- [ ] **TASK-146** Security audit (Both)
  - OWASP checks
  - Dependency scanning
  - Estimate: 3h

**Acceptance Criteria:**
- ✅ Authentication required for API
- ✅ HTTPS enabled
- ✅ All inputs validated
- ✅ No critical security issues

---

## Epic 10: Launch & Iteration

### Sprint 12: Deployment (Week 18+)

#### Story 10.1: Initial Deployment
**As a product owner, I want the app deployed to production.**

**Tasks:**
- [ ] **TASK-147** 🔴 Set up production server/cloud (Person A)
  - Provision infrastructure
  - Estimate: 4h
  
- [ ] **TASK-148** 🔴 Deploy to production (Person A)
  - Run deployment
  - Verify all services
  - Estimate: 3h
  
- [ ] **TASK-149** 🟡 Set up backup and restore (Person B)
  - Database backups
  - Recovery procedures
  - Estimate: 3h
  
- [ ] **TASK-150** Smoke tests in production (Both)
  - Test all workflows
  - Estimate: 2h

**Acceptance Criteria:**
- ✅ App deployed successfully
- ✅ All services running
- ✅ Smoke tests pass
- ✅ Backups configured

---

#### Story 10.2: Pilot Launch
**As a product owner, I want to onboard pilot users.**

**Tasks:**
- [ ] **TASK-151** Create user onboarding materials (Person B)
  - User guide
  - FAQ
  - Estimate: 3h
  
- [ ] **TASK-152** Onboard pilot users (Both)
  - 5-10 users
  - Estimate: 2h
  
- [ ] **TASK-153** Monitor pilot usage (Both)
  - Track errors
  - Collect feedback
  - Estimate: Ongoing

**Acceptance Criteria:**
- ✅ Pilot users onboarded
- ✅ Feedback collected
- ✅ No critical issues

---

#### Story 10.3: Iteration & Improvement
**As a product owner, I want to improve based on feedback.**

**Tasks:**
- [ ] **TASK-154** Fix bugs from pilot (Both)
  - Prioritize critical issues
  - Estimate: Varies
  
- [ ] **TASK-155** Improve prompts based on real data (Person A)
  - Refine LLM prompts
  - Estimate: Ongoing
  
- [ ] **TASK-156** Add new features (Both)
  - Based on user requests
  - Estimate: Varies

**Acceptance Criteria:**
- ✅ Critical bugs fixed
- ✅ User satisfaction improving
- ✅ System stable

---

## Task Dependencies & Parallelization Guide

### Phase 1: Foundation (Week 1-2)
**Parallel Work:**
- Person A: TASK-001, 004, 005, 007-008, 012, 013, 016-019, 023-024, 026-027, 029, 031
- Person B: TASK-002, 003, 006, 009-011, 014-015, 020-022, 025, 028, 030, 031

**Critical Path:** TASK-001 → 007 → 018 → 024 → 027 → 029

---

### Phase 2: Supervisor (Week 3)
**Parallel Work:**
- Person A: TASK-032-034, 037-038, 040-041
- Person B: TASK-035-036, 039, 041

**Critical Path:** TASK-032 → 033 → 037 → 039 → 040

---

### Phase 3: Symptoms Graph (Week 4-5)
**Parallel Work:**
- Person A: TASK-042-043, 046-047, 049-050
- Person B: TASK-044-045, 048, 050

**Critical Path:** TASK-042 → 046 → 048 → 049

---

### Remaining Phases:
Similar parallelization patterns - see individual sprint sections above.

---

## GitHub Project Board Setup

### Columns:
1. **Backlog** - All tasks not yet started
2. **Ready** - Tasks ready to be worked on (dependencies met)
3. **In Progress** - Currently being worked on
4. **In Review** - Code complete, awaiting review
5. **Testing** - In testing phase
6. **Done** - Completed and merged

### Labels:
- `priority:critical` - Must be done first
- `priority:high` - Important
- `priority:medium` - Normal priority
- `priority:low` - Nice to have
- `type:feature` - New feature
- `type:bug` - Bug fix
- `type:test` - Testing
- `type:docs` - Documentation
- `epic:foundation` - Epic 1
- `epic:supervisor` - Epic 2
- ... (one per epic)
- `can-parallelize` - Can work in parallel
- `person-a` - Assigned to Person A
- `person-b` - Assigned to Person B

### Milestones:
- **M1: Foundation Complete** (Week 2)
- **M2: Supervisor Ready** (Week 3)
- **M3: First Graph Working** (Week 5)
- **M4: Safety Implemented** (Week 6)
- **M5: All Graphs Complete** (Week 9)
- **M6: RAG Integrated** (Week 11)
- **M7: Memory & Progress** (Week 13)
- **M8: Testing Complete** (Week 15)
- **M9: Production Ready** (Week 17)
- **M10: Deployed** (Week 18)

---

## Estimated Total Time

- **Person A:** ~200 hours
- **Person B:** ~200 hours
- **Total:** ~400 person-hours
- **Calendar Time:** 18 weeks (4.5 months)

---

## Getting Started

1. Import tasks into GitHub Issues
2. Create project board with columns
3. Assign labels and milestones
4. Start with TASK-001 (Person A) and TASK-002 (Person B)
5. Daily standup to sync progress
6. Weekly review to adjust priorities

Good luck! 🚀
