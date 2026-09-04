# EDITH-001 — Architecture Gap Analysis

**Author:** Mannan Shah (System Designer & Solutions Architect)  
**Project:** EDITH (Enhanced Distributed Intelligent Task Handler)  
**Date:** August 30, 2026  
**Status:** Proposed Baseline — Subject to EDITH-000 Approval  

---

## 1. Executive Summary

This document presents the **Architecture Gap Analysis** for EDITH as part of **EDITH-001 (Sprint 1)**. It establishes the actual current state of the codebase, identifies missing architectural components, highlights technical and contract risks, documents dependencies on EDITH-000 (Core EDITH Specification), and outlines the recommended minimal architecture direction.

---

## 2. Current Repository State

An inspection of the official repository (`https://github.com/Prempujara/edith`) confirms a structured **monorepo layout** containing placeholder directories and basic documentation shells.

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

* **Framework:** Target framework is **FastAPI** (Python 3.11+).
* **Actual Repository State:** Placeholder shell (`apps/backend/README.md`). No active Python source code, routes, models, or entry points exist in the repository yet.
* **Intended Baseline:** FastAPI application with standard health/documentation routes (`/`, `/health`, `/docs`).
* **Missing Baseline Architectural Capabilities:**
  * Application entrypoint (`main.py`)
  * Task API route handlers (Task creation and status endpoints — exact endpoint names, paths, versioning, and schemas to be finalized by EDITH-000)
  * Internal event publication/dispatch mechanism (if required by the approved EDITH event model)
  * In-memory task state tracking behind a replaceable persistence boundary
  * CORS middleware configuration
  * Exception mapping and error response middleware

---

## 4. Existing Frontend Assessment

* **Framework:** Target framework is **Next.js** (React / TypeScript).
* **Actual Repository State:** Placeholder shell (`apps/frontend/README.md`). No Next.js application structure (`app/` or `pages/`), components, UI state management, or API clients exist in the repository yet.
* **Missing Baseline Architectural Capabilities:**
  * Task submission form (Text / Voice prompt input UI)
  * Task status dashboard (Configurable periodic polling interface)
  * Execution log / telemetry visualizer
  * Client-side speech synthesis and recognition hooks

---

## 5. Existing Documentation & Specification Assessment

* **Current Documentation:** Minimal root `README.md` and package `README.md` shells.
* **EDITH-000 Specification Status:** **Missing / Unapproved**. No approved specification file exists in `docs/` or `packages/shared`.
* **Contract Impact:** As mandated by **Rule 8**, all data structures, API endpoints, lifecycle states, and event schemas must be explicitly marked as `PROPOSED — REQUIRES EDITH-000 APPROVAL`.

---

## 6. Architecture Gap Matrix

| Architectural Subsystem | Current Repository State | Missing Architectural Capabilities | Impact / Risk |
| :--- | :--- | :--- | :--- |
| **EDITH API Boundary** | Placeholder README | REST endpoints, payload validation, CORS rules (Paths and schemas: `PROPOSED — REQUIRES EDITH-000 APPROVAL`) | **High** — Blocks frontend-backend integration contract |
| **Orchestrator** | Non-existent | Task workflow manager, task routing logic, agent dispatching, error boundary | **High** — Core execution engine undefined |
| **Coding Agent Boundary** | Placeholder README | Agent execution/decision interface and tool-request boundary | **High** — Agent boundary must remain isolated from direct filesystem writes |
| **Tool / Repo Layer** | Non-existent | Controlled Tool / Repository Execution boundary with validation, allowed-operation restrictions, timeouts, and safety checks | **Medium** — Workspace path safety missing |
| **Internal Event System** | Non-existent | Internal event publication/dispatch mechanism for decoupled observer updates | **Medium** — Frontend, Slack, and Voice observers require decoupled notifications |
| **Voice Adapter Boundary** | Placeholder README | Speech-to-Text (STT) and Text-to-Speech (TTS) adapter interfaces | **Medium** — Requires vendor-neutral adapter to satisfy ₹0 budget |
| **Slack Adapter Boundary** | Placeholder README | Event-driven notification adapter for Slack alerts | **Low** — Pure output consumer; isolated boundary |
| **State & Persistence** | Non-existent | Task state store (In-memory state for MVP behind a replaceable repository boundary) | **Low** — In-memory state sufficient for MVP |

---

## 7. Technical & Project Risks

1. **Risk 1: Over-Engineering & Vendor Lock-In (Violation of ₹0 Budget)**
   * *Mitigation:* The AI/model integration must use a replaceable provider boundary. Prefer local or open-source execution where practical. Free-tier external providers may be evaluated only if necessary, but the core EDITH architecture must not depend on a paid provider or on a specific vendor. *(Example implementation options: Ollama, OpenRouter, Groq — listed as options, not architecture requirements).*
2. **Risk 2: Coupling Orchestrator to Infrastructure & UI**
   * *Mitigation:* Strict boundary definition (ADR-003). Orchestrator owns task workflow; UI, Slack, and Voice act purely as external observers/adapters.
3. **Risk 3: Uncontrolled Workspace Operations in Tool Layer**
   * *Mitigation:* Enforce a controlled Tool / Repository Execution boundary with path validation, workspace restrictions, and timeouts.
4. **Risk 4: Realtime Infrastructure Complexity**
   * *Mitigation:* Adopt configurable short-interval client HTTP polling for MVP dashboard status updates instead of complex WebSockets (ADR-002).

---

## 8. Dependencies on EDITH-000 (Core Specification)

The following items are explicitly marked as **PROPOSED — REQUIRES EDITH-000 APPROVAL**:

* **Proposed Task Lifecycle:** `CREATED` $\rightarrow$ `QUEUED` $\rightarrow$ `IN_PROGRESS` $\rightarrow$ `COMPLETED` / `FAILED` *(PROPOSED — REQUIRES EDITH-000 APPROVAL)*
* **Proposed Event Catalog:** `task.created`, `task.started`, `agent.assigned`, `tool.executed`, `task.completed`, `task.failed` *(PROPOSED — REQUIRES EDITH-000 APPROVAL)*
* **Proposed REST Endpoint Signatures:** `POST /api/v1/tasks`, `GET /api/v1/tasks/{id}`, `GET /api/v1/tasks` *(PROPOSED — REQUIRES EDITH-000 APPROVAL)*
* **Proposed JSON Request/Response Schemas** *(PROPOSED — REQUIRES EDITH-000 APPROVAL)*

---

## 9. Recommended Architectural Direction

To achieve Sprint 1 goals while maintaining strict zero-budget compliance:

1. **Architecture Pattern:** **Modular Monolith** hosted within FastAPI backend (`apps/backend`).
2. **Communication Strategy:** Clean REST API over HTTP with JSON payloads; client-side configurable periodic polling for task status updates.
3. **Persistence Strategy:** In-memory task state for the MVP behind a replaceable repository boundary.
4. **Voice Strategy:** Provider-independent STT/TTS adapter interfaces. Client-side browser-native speech capabilities (SpeechRecognition + SpeechSynthesis) may be evaluated as a zero-cost MVP implementation option.
5. **Slack Strategy:** Event-driven notification adapter using zero-cost incoming webhooks.
