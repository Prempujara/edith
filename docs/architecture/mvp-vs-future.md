# EDITH-001 — MVP vs. Future Architecture Expansion

**Author:** Mannan Shah (System Designer & Solutions Architect)  
**Project:** EDITH (Enhanced Distributed Intelligent Task Handler)  
**Date:** August 30, 2026  
**Status:** Complete / Proposed Blueprint  

---

## 1. Overview

This document clearly demarcates the **Sprint 1 & 2 MVP Scope** from **Future Post-MVP Architecture Capabilities**. Establishing explicit boundaries prevents scope creep and ensures the team delivers a working, zero-budget college project without premature optimization or unnecessary infrastructure overhead.

---

## 2. Scope Demarcation Matrix

| System Domain | Sprint 1 & 2 MVP Scope (College SPM Release) | Future Post-MVP Scope (Deferred) |
| :--- | :--- | :--- |
| **System Style** | **Modular Monolith** in single Python backend process | Distributed Microservices architecture |
| **Persistence** | **In-Memory TaskStore** (`dict` behind `ITaskRepository`) | Persistent PostgreSQL / SQLite relational database |
| **Realtime Strategy** | **HTTP Short Polling** (2s interval `GET /api/v1/tasks/{id}`) | WebSockets / Server-Sent Events (SSE) |
| **Agents** | **Single Coding Agent** (`packages/agents/coding`) | Multi-agent collaboration (Testing, Security, DevOps agents) |
| **Voice Processing** | **Browser Web Speech API** (Client STT/TTS) | Server-side Whisper / Cloud Neural TTS (ElevenLabs) |
| **Slack Integration** | **Outgoing Webhook Adapter** (Notification consumer) | Interactive 2-Way Slack Bot (Slash commands, Socket Mode) |
| **Authentication** | **None / Open Local API** (Development mode) | JWT / OAuth2 Multi-Tenant Authentication |
| **Message Queue** | **In-Process `asyncio.Queue` / PyPubSub** | External Redis / RabbitMQ / Celery distributed broker |
| **Deployment** | **Local Development Server** (`uvicorn` + `npm run dev`) | Kubernetes (k8s) / Cloud Container Services |
| **Budget** | **Hard Constraint: ₹0** | Paid SaaS / Managed Infrastructure |

---

## 3. MVP Flow Blueprint

```text
Voice / Text Command
        ↓
    EDITH API
        ↓
   Orchestrator
        ↓
   Coding Agent
        ↓
Tool / Repository Execution
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
The `TaskStore` is accessed exclusively through the abstract `ITaskRepository` interface. To introduce PostgreSQL or SQLite in a future sprint, developers simply implement `SQLTaskRepository(ITaskRepository)` without altering the Orchestrator or API routes.

### 4.2 Migration Path: Single Agent $\rightarrow$ Multi-Agent Ensemble
The `Orchestrator` relies on an abstract `BaseAgent` class (`packages/agents/base`). Additional agents (e.g., `ReviewAgent`, `TestAgent`) can be added as new classes under `packages/agents/` and registered with the Orchestrator's agent dispatcher.

### 4.3 Migration Path: Web Polling $\rightarrow$ WebSockets
The API gateway exposes cleanly separated event topics. Replacing HTTP polling with WebSockets only requires wrapping the internal `EventBus` subscriber in a FastAPI WebSocket endpoint.

---

## 5. Architectural Guardrails (Scope Protections)

To ensure success for the college presentation:

1. **No External Infrastructure Dependencies:** The MVP must start with a single terminal command without requiring Docker Compose containers, PostgreSQL instances, or Redis brokers unless explicitly requested.
2. **No Paid API Lock-In:** Core features must function offline or using free open-source models.
3. **No Premature Microservices:** All internal packages remain inside the single monorepo and run inside a unified backend runtime.
