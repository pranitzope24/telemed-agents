# Architecture

## Overview

The Agentic AI Chatbot is a multi-agent system designed for telemedicine workflows, combining symptom analysis, Ayurvedic consultation, doctor matching, prescription management, and progress monitoring. The architecture follows a supervisor-orchestrated graph pattern where specialized sub-graphs handle domain-specific workflows.

## Core Components

### 1. API Layer (`app/api/`)
- **chat.py**: Main conversation endpoint; handles user messages and session management
- **session.py**: Session lifecycle management (create, resume, terminate)
- **webhook.py**: Webhook handlers for external integrations
- **health.py**: Health check and monitoring endpoints

### 2. Supervisor (`app/supervisor/`)
- **supervisor_graph.py**: Top-level orchestrator that routes requests to appropriate sub-graphs
- **router.py**: Routing logic based on intent and risk classification
- **intent_classifier.py**: Classifies user intent (symptom inquiry, dosha consultation, prescription, follow-up)
- **risk_classifier.py**: Assesses medical risk level (low, medium, high, emergency)
- **constants.py**: Shared constants for intent types, risk levels, graph names

### 3. Sub-Graphs (`app/graphs/`)

Each graph is a self-contained pipeline with:
- `graph.py`: Graph orchestration and node flow
- `nodes.py`: Individual processing nodes
- `state.py`: Graph-specific state models
- `prompts.py`: LLM prompts for the graph

**Available Graphs:**
- **symptoms_graph**: Symptom collection, normalization, triage
- **dosha_graph**: Ayurvedic questionnaire and dosha inference
- **doctor_matching_graph**: Doctor search, filtering, booking
- **prescription_graph**: Prescription drafting, review, approval
- **progress_graph**: Progress tracking, trend analysis, follow-ups
- **emergency_graph**: Emergency detection and escalation

### 4. Agents (`app/agents/`)

Atomic reasoning units that perform specific tasks:
- **symptom_triage_agent.py**: Analyzes symptoms and determines urgency
- **questionnaire_agent.py**: Manages dynamic questionnaires
- **dosha_inference_agent.py**: Calculates Ayurvedic dosha profile
- **prescription_draft_agent.py**: Generates prescription drafts
- **drug_interaction_agent.py**: Checks for drug interactions
- **trend_analysis_agent.py**: Analyzes health trends from logs
- **followup_agent.py**: Generates follow-up recommendations
- **emergency_response_agent.py**: Handles emergency situations

### 5. Tools (`app/tools/`)

Integrations with backend services:
- **doctor_service.py**: Doctor search and availability
- **booking_service.py**: Appointment booking
- **prescription_service.py**: Prescription storage and retrieval
- **notification_service.py**: Email/SMS notifications
- **analytics_service.py**: Usage analytics and reporting
- **user_service.py**: User profile management

### 6. RAG System (`app/rag/`)

Retrieval-Augmented Generation for knowledge grounding:
- **ayurveda/**: Ayurvedic knowledge base (loader, retriever, prompts)
- **medical/**: Medical reference materials (loader, retriever)
- **safety/**: Safety rules and clinical guidelines (YAML/Markdown)
- **vector_store.py**: Vector database interface

### 7. Safety Layer (`app/safety/`)

Guardrails and compliance:
- **safety_agent.py**: Overall safety orchestration
- **compliance_checker.py**: Regulatory compliance validation
- **hallucination_detector.py**: Detects and prevents hallucinations
- **emergency_detector.py**: Real-time emergency detection
- **medical_disclaimer.py**: Ensures proper disclaimers

### 8. Memory & State (`app/memory/`, `app/state/`)

**Memory types:**
- **short_term.py**: Session-scoped working memory (Redis)
- **long_term.py**: Persistent user history (Database)
- **episodic.py**: Past conversation episodes
- **session_memory.py**: Current session transcript

**State models:**
- **base_state.py**: Base state class and mixins
- **user_state.py**: User profile state
- **medical_state.py**: Medical context state
- **conversation_state.py**: Conversation flow state
- **graph_state.py**: Active graph tracking

### 9. Configuration (`app/config/`)

- **settings.py**: Application settings
- **llm.py**: LLM model configuration
- **embeddings.py**: Embedding model configuration
- **models.py**: Model registry
- **feature_flags.py**: Feature toggles

### 10. Utilities (`app/utils/`)

- **logger.py**: Logging utilities
- **ids.py**: ID generation
- **time.py**: Time utilities
- **retry.py**: Retry logic with exponential backoff

## Data Flow

### New Query Flow
1. User message → `api/chat.py`
2. Intent classification → `supervisor/intent_classifier.py`
3. Risk assessment → `supervisor/risk_classifier.py`
4. Graph routing → `supervisor/router.py`
5. Graph execution → `graphs/*/graph.py` + `nodes.py`
6. Agent invocation → `agents/*.py`
7. Tool calls → `tools/*.py`
8. Safety checks → `safety/*.py`
9. Response generation → back through supervisor → `api/chat.py`

### Follow-up Flow
1. User message → `api/chat.py`
2. Load session state (active_graph, active_node)
3. Resume graph at saved node
4. Process user input, update state
5. Continue or pause with next question
6. Return response

## State Management

### Short-term (Redis)
- **Key pattern**: `session:{session_id}:session_state`, `session:{session_id}:{graph}_state`
- **Contents**: Active graph, current node, intent, risk level, recent turns (last N messages), handoff data
- **TTL**: Configurable (e.g., 1 hour of inactivity)

### Long-term (PostgreSQL)
- **Tables**: users, sessions, questionnaire_answers, prescriptions, doctor_matches, progress_logs, audit_log
- **Purpose**: Durable clinical records, compliance, analytics

### Vector Store (pgvector or dedicated DB)
- **Contents**: Embeddings of notes, prescriptions, Ayurvedic texts, medical references
- **Purpose**: RAG retrieval for context-aware responses

## Security & Compliance

- All medical data encrypted at rest and in transit
- Audit logging for all critical actions (prescriptions, emergency escalations)
- Safety checks before every LLM call and action
- Hallucination detection on medical recommendations
- Proper disclaimers appended to all medical advice

## Scalability

- **Stateless API layer**: Horizontal scaling via load balancer
- **Redis for session state**: Fast, distributed cache
- **Database connection pooling**: Efficient resource usage
- **Async graph execution**: Non-blocking I/O for tool calls
- **Background jobs**: Progress monitoring, analytics via task queue

## Technology Stack

- **Framework**: FastAPI (async Python web framework)
- **LLM**: Configurable (OpenAI, Anthropic, or local models)
- **State**: Redis (ephemeral), PostgreSQL (durable)
- **Vector DB**: pgvector or Pinecone/Qdrant
- **Orchestration**: LangGraph for graph execution
- **Monitoring**: Prometheus + Grafana (optional)
- **Deployment**: Docker + Kubernetes (or single-server Docker Compose)
