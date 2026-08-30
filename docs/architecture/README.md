# EDITH System Architecture Documentation (EDITH-001)

**System Designer & Solutions Architect:** Mannan Shah  
**Project:** EDITH (Enhanced Distributed Intelligent Task Handler)  
**Sprint:** Sprint 1 — Technical Architecture Blueprint  
**Date:** August 30, 2026  

---

## 1. Executive Overview

Welcome to the official **EDITH System Architecture Documentation**. This directory contains the complete technical blueprint created by **Mannan Shah** under **EDITH-001** to make the EDITH system implementation-ready for Sprint 2.

EDITH is a multi-agent AI task-handling platform for a college Software Project Management (SPM) project. The system is designed around a **Modular Monolith** pattern operating under a strict **₹0 budget constraint**.

---

## 2. Architecture Documentation Sitemap

```text
docs/architecture/
├── README.md                              # Main Architecture Navigation & Guide (This File)
├── architecture-gap-analysis.md           # Baseline Inspection & Gap Identification
├── system-architecture.md                 # High-Level Blueprint & Subsystem Decomposition
├── component-responsibilities.md          # Component Specifications & Responsibility Matrix
├── request-execution-flow.md              # End-to-End Sequence Flow & Step-by-Step Guide
├── frontend-backend-architecture.md       # Next.js / FastAPI Integration, CORS, & Polling
├── event-architecture.md                  # Event Bus, Topic Catalog, & Subscriber Interfaces
├── error-failure-flow.md                  # Fault Isolation, Error Modes, & Recovery Strategies
├── voice-architecture.md                  # Browser Web Speech STT/TTS Integration Boundary
├── slack-architecture.md                  # Event-Driven Slack Webhook Integration Boundary
├── mvp-vs-future.md                       # Sprint 1/2 MVP Scope vs Post-MVP Expansion
├── EDITH-001-completion-checklist.md      # Acceptance Criteria Verification Matrix
└── adr/                                   # Architecture Decision Records
    ├── ADR-001-architecture-style.md      # Modular Monolith vs Microservices
    ├── ADR-002-communication-strategy.md  # Short HTTP Polling vs WebSockets
    ├── ADR-003-orchestrator-boundary.md   # Orchestrator SRP & Anti-Pattern Boundaries
    ├── ADR-004-agent-tool-boundary.md     # Sandboxed Tool Execution Layer Boundary
    ├── ADR-005-persistence-decision.md    # In-Memory Task Storage for MVP
    ├── ADR-006-voice-integration.md       # Browser Web Speech API Strategy
    ├── ADR-007-slack-integration.md       # Decoupled Slack Webhook Adapter Strategy
    └── ADR-008-authentication-decision.md # Deferred Authentication Strategy
```

---

## 3. Traceability Matrix

The following matrix maps architectural decisions directly to project constraints and technical requirements:

| Architecture Decision | Requirement / Rationale | Impacted Subsystem | Document Reference |
| :--- | :--- | :--- | :--- |
| **Modular Monolith** | Single-process deployment for ₹0 budget & low complexity | Whole Backend (`apps/backend`) | [ADR-001](file:///c:/Users/Mannan/OneDrive/Documents/ProjectSPM/docs/architecture/adr/ADR-001-architecture-style.md) |
| **Short HTTP Polling (2s)** | Eliminate WebSocket state complexity & connection drops | Frontend / API Gateway | [ADR-002](file:///c:/Users/Mannan/OneDrive/Documents/ProjectSPM/docs/architecture/adr/ADR-002-communication-strategy.md) |
| **Orchestrator SRP Boundary** | Prevent "God Object" anti-pattern in workflow engine | Core Orchestrator Engine | [ADR-003](file:///c:/Users/Mannan/OneDrive/Documents/ProjectSPM/docs/architecture/adr/ADR-003-orchestrator-boundary.md) |
| **Sandboxed Tool Layer** | Prevent path traversal attacks and system file corruption | Tool Sandbox Execution | [ADR-004](file:///c:/Users/Mannan/OneDrive/Documents/ProjectSPM/docs/architecture/adr/ADR-004-agent-tool-boundary.md) |
| **In-Memory TaskStore** | Avoid database setup & migration overhead in college MVP | State & Persistence | [ADR-005](file:///c:/Users/Mannan/OneDrive/Documents/ProjectSPM/docs/architecture/adr/ADR-005-persistence-decision.md) |
| **Browser Web Speech API** | Provide STT/TTS without paid cloud service subscriptions | Voice Integration Package | [ADR-006](file:///c:/Users/Mannan/OneDrive/Documents/ProjectSPM/docs/architecture/adr/ADR-006-voice-integration.md) |
| **Slack Webhook Adapter** | Decouple channel alerts from core task execution loops | Slack Integration Package | [ADR-007](file:///c:/Users/Mannan/OneDrive/Documents/ProjectSPM/docs/architecture/adr/ADR-007-slack-integration.md) |
| **Deferred Authentication** | Focus developer effort on core agent orchestration | API Security Gateway | [ADR-008](file:///c:/Users/Mannan/OneDrive/Documents/ProjectSPM/docs/architecture/adr/ADR-008-authentication-decision.md) |

---

## 4. System Constraints

### 4.1 Hard Constraints
* **₹0 Operational Budget:** Hard financial constraint. Absolutely no mandatory paid cloud APIs, paid voice services, paid SaaS databases, or paid monitoring tools.
* **Open-Source / Free Technologies Only:** Local Python execution, browser Web Speech API, open-source libraries, free incoming Slack webhooks.
* **Monorepo Compatibility:** Must fit cleanly into the existing `apps/` and `packages/` repository layout.
* **No Feature Implementation in Sprint 1:** Sprint 1 is reserved exclusively for architecture blueprints and specifications.

### 4.2 Soft Constraints
* **Maintainability:** Clear separation between API, Orchestrator, Agent logic, and low-level tools.
* **Replaceability:** Voice and Slack modules encapsulated behind abstract interface adapters.
* **Future Extensibility:** Simple migration path to databases or microservices post-MVP.

---

## 5. Contract Verification Rule & Approval Status

In compliance with **Rule 8 (IMPORTANT CONTRACT RULE)**, because **EDITH-000 (Core Specification)** is currently unapproved/missing in the baseline repository:

* All task lifecycle states (`CREATED`, `QUEUED`, `IN_PROGRESS`, `COMPLETED`, `FAILED`) are marked as **PROPOSED**.
* All event names (`task.created`, `task.started`, `tool.executed`, `task.completed`, `task.failed`) are marked as **PROPOSED**.
* All API endpoint paths (`/api/v1/tasks`) and request/response payloads are marked as **PROPOSED**.

Upon formal release and approval of EDITH-000, these proposed schemas will be verified and updated accordingly.
