# EDITH-001 — MVP vs. Future Architecture Expansion

**Author:** Mannan Shah (System Designer & Solutions Architect)  
**Project:** EDITH (Enhanced Distributed Intelligent Task Handler)  
**Date:** August 30, 2026  
**Status:** Proposed Specification — Subject to EDITH-000 Approval  

---

## 1. Overview

This document clearly demarcates the **Sprint 1 & 2 MVP Scope** from **Future Post-MVP Architecture Capabilities**. Establishing explicit boundaries prevents scope creep and ensures the team delivers a working, zero-budget college project without premature optimization or unnecessary infrastructure overhead.

---

## 2. Scope Demarcation Matrix

| System Domain | Sprint 1 & 2 MVP Scope (College SPM Release) | Future Post-MVP Scope (Deferred) |
| :--- | :--- | :--- |
| **System Style** | **Modular Monolith** in single Python backend process | Distributed Microservices architecture |
| **Persistence** | **In-Memory Task State Store** behind a replaceable repository boundary | Persistent PostgreSQL / SQLite relational database |
| **Realtime Strategy** | **Configurable Periodic Short HTTP Polling** | WebSockets / Server-Sent Events (SSE) |
| **Agents** | **Single Coding Agent** (`packages/agents/coding`) | Multi-agent collaboration (Testing, Security, DevOps agents) |
| **Voice Processing** | **Provider-Independent STT/TTS Interfaces** (Browser Web Speech API as zero-cost option) | Server-side Whisper / Cloud Neural TTS |
| **Slack Integration** | **Outgoing Webhook Adapter** (Notification consumer) | Interactive 2-Way Slack Bot (Slash commands, Socket Mode) |
| **Authentication** | **Deferred / Open Local API** (Development mode) | JWT / OAuth2 Multi-Tenant Authentication |
| **Message Broker** | **In-Process `asyncio` Event Dispatcher** | External Redis / RabbitMQ / Celery distributed broker |
| **Deployment** | **Local Development Server** (`uvicorn` + `npm run dev`) | Kubernetes (k8s) / Cloud Container Services |
| **Budget** | **Hard Constraint: ₹0** | Paid SaaS / Managed Infrastructure |

---

## 3. MVP Conceptual Flow Blueprint

```text
Voice / Text Command
        ↓
    EDITH API
        ↓
   Orchestrator
        ↓
   Coding Agent
        ↓
Tool / Repository Execution Boundary
        ↓
      Result
        ↓
    Dashboard
        ↓
   Voice Response
        ↓
 Slack Notification
```

---

## 4. Future Architecture Migration Paths

While Sprint 1 & 2 focus strictly on the MVP, the modular monolith architecture includes explicit extension points to enable future enhancements without complete system rewrites:

### 4.1 Migration Path: In-Memory Store $\rightarrow$ Relational Database
Task state is accessed through an abstract repository interface boundary. To introduce PostgreSQL or SQLite in a future sprint, developers simply implement a SQL repository adapter without altering Orchestrator or API routes.

### 4.2 Migration Path: Single Agent $\rightarrow$ Multi-Agent Ensemble
The `Orchestrator` relies on an abstract agent boundary (`packages/agents/base`). Additional agents (e.g., `ReviewAgent`, `TestAgent`) can be added as new modules under `packages/agents/` and registered with the Orchestrator's agent dispatcher.

### 4.3 Migration Path: Periodic Polling $\rightarrow$ WebSockets
The API gateway exposes decoupled event topics. Replacing periodic polling with WebSockets requires wrapping the internal event publisher in a FastAPI WebSocket endpoint.

---

## 5. Architectural Guardrails (Scope Protections)

To ensure success for the college presentation:

1. **No External Infrastructure Dependencies:** The MVP starts with a single terminal command without requiring Docker Compose containers, PostgreSQL instances, or Redis brokers unless explicitly requested.
2. **No Mandatory Paid API Lock-In:** Core features function offline or using open-source models.
3. **No Premature Microservices:** All internal packages remain inside the single monorepo and run inside a unified backend runtime.
