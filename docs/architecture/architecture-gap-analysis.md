# EDITH-001 — Architecture Gap Analysis

**Author:** Mannan Shah (System Designer & Solutions Architect)  
**Project:** EDITH (Enhanced Distributed Intelligent Task Handler)  
**Date:** August 30, 2026  
**Status:** Complete / Proposed Baseline  

---

## 1. Executive Summary

This document presents the **Architecture Gap Analysis** for EDITH as part of **EDITH-001 (Sprint 1)**. It establishes the current state of the codebase, identifies missing architectural components, highlights technical and contract risks, documents dependencies on EDITH-000 (Core EDITH Specification), and outlines the recommended minimal architecture direction.

---

## 2. Current Repository State

An inspection of the official repository (`https://github.com/Prempujara/edith`) reveals a structured **monorepo layout** containing placeholder directories and basic documentation shells.

### Directory Structure Overview
```text
edith/
├── .env.example              # Environment variable template placeholder
├── docker-compose.yml        # Docker Compose configuration placeholder
├── README.md                 # Root README placeholder
├── apps/
│   ├── backend/              # Reserved for FastAPI application (README placeholder only)
│   └── frontend/             # Reserved for Next.js application (README placeholder only)
├── packages/
│   ├── agents/
│   │   ├── base/             # Base agent package placeholder
│   │   └── coding/           # Coding agent package placeholder
│   ├── shared/               # Shared types/utilities placeholder
│   ├── slack/                # Slack integration package placeholder
│   └── voice/                # Voice integration package placeholder
└── docs/
    └── .gitkeep              # Empty documentation root
```

---

## 3. Existing Backend Assessment

* **Framework:** Standardized on **FastAPI** (Python 3.11+ target).
* **Current State:** Pure placeholder (`apps/backend/README.md`). No active Python source code, routes, models, or entry points exist yet.
* **Intended Baseline:** FastAPI with standard endpoints (`/`, `/health`, `/docs` Swagger UI).
* **Missing Baseline Capabilities:**
  * Application entrypoint (`main.py`)
  * Task route handlers (`/api/v1/tasks`)
  * Event broker / queue implementation
  * In-memory task repository
  * CORS middleware configuration
  * Exception mapping and error response middleware

---

## 4. Existing Frontend Assessment

* **Framework:** Standardized on **Next.js** (React / TypeScript target).
* **Current State:** Pure placeholder (`apps/frontend/README.md`). No Next.js application structure (`app/` or `pages/`), components, UI state management, or API clients exist yet.
* **Missing Baseline Capabilities:**
  * Task submission form (Text / Voice prompt input)
  * Realtime or polling task status dashboard
  * Execution log / telemetry viewer
  * Voice synthesis/recognition hook wrappers

---

## 5. Existing Documentation & Specification Assessment

* **Current Documentation:** Minimal root `README.md` and package `README.md` shells.
* **EDITH-000 Specification Status:** **Missing / Unapproved**. No approved specification file exists in `docs/` or `packages/shared`.
* **Contract Impact:** As mandated by **Rule 8**, all data structures, API endpoints, lifecycle states, and event schemas must be explicitly marked as `PROPOSED / REQUIRES EDITH-000 APPROVAL`.

---

## 6. Architecture Gap Matrix

| Architectural Subsystem | Current State | Missing Requirements | Impact / Risk |
| :--- | :--- | :--- | :--- |
| **EDITH API Boundary** | Non-existent | REST endpoints, request validation, CORS rules, API versioning schema | **High** — Blocks frontend-backend integration in Sprint 2 |
| **Orchestrator** | Non-existent | Task lifecycle manager, routing logic, agent dispatching, error fallback | **High** — Core execution engine undefined |
| **Coding Agent** | Non-existent | Context builder, LLM prompt pipeline, tool request protocol, execution parser | **High** — Agent boundary must remain isolated from direct repo writes |
| **Tool / Repo Layer** | Non-existent | Sandboxed execution interface (file read/write, shell execution, git inspection) | **Medium** — Tool safety and rollback missing |
| **Event System** | Non-existent | Event definitions, publisher/subscriber mechanism, listener bindings | **Medium** — Frontend and Slack updates rely on event propagation |
| **Voice Adapter** | Non-existent | STT command ingest & TTS audio response adapters | **Medium** — Needs vendor-neutral adapter to satisfy ₹0 budget |
| **Slack Integration** | Non-existent | Event subscriber to send webhooks/messages to Slack channels | **Low** — Pure output consumer; isolated boundary |
| **State & Persistence** | Non-existent | Task state store (In-memory vs Database) | **Low** — In-memory state sufficient for MVP |

---

## 7. Technical & Project Risks

1. **Risk 1: Over-Engineering / Paid Service Sprawl (Violation of ₹0 Budget)**
   * *Mitigation:* Explicitly mandate open-source LLM providers (e.g., local Ollama, free-tier OpenRouter/Groq) and browser-native Web Speech API for voice.
2. **Risk 2: Coupling Orchestrator to Infrastructure & UI**
   * *Mitigation:* Strict boundary definition (ADR-003). Orchestrator owns task flow; UI, Slack, and Voice act purely as external observers/adapters.
3. **Risk 3: Unbounded Code Execution in Tool Layer**
   * *Mitigation:* Restrict Tool Execution Layer to local sandbox boundaries with standard timeouts and safety checks.
4. **Risk 4: Realtime Infrastructure Complexity**
   * *Mitigation:* Adopt short HTTP polling for MVP dashboard status updates instead of complex WebSockets (ADR-002).

---

## 8. Dependencies on EDITH-000 (Core Specification)

The following items are defined as **PROPOSED** pending formal approval of **EDITH-000**:

* Task Lifecycle States: `CREATED` $\rightarrow$ `QUEUED` $\rightarrow$ `IN_PROGRESS` $\rightarrow$ `COMPLETED` / `FAILED`
* Event Schema & Event Names (`task.created`, `task.started`, `agent.assigned`, `tool.executed`, `task.completed`, `task.failed`)
* REST Endpoint Signatures (`POST /api/v1/tasks`, `GET /api/v1/tasks/{id}`, `GET /api/v1/tasks`)
* JSON Request/Response Payload Structures

---

## 9. Recommended Architectural Direction

To achieve Sprint 1 goals while maintaining strict zero-budget compliance:

1. **Architecture Pattern:** **Modular Monolith** hosted within FastAPI backend (`apps/backend`).
2. **Communication Strategy:** Clean REST API over HTTP with JSON payloads; client-side short polling for task status (every 2 seconds).
3. **Persistence:** In-Memory Task Repository behind an abstract repository interface (`ITaskRepository`).
4. **Voice Strategy:** Client-side browser Web Speech API (SpeechRecognition + SpeechSynthesis) with backend fallback interfaces.
5. **Slack Strategy:** Async HTTP webhook adapter triggered by task events.
