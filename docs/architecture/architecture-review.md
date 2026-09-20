# EDITH-001 — Architecture Review of Current Implementation

**Author:** Mannan Shah (System Designer & Solutions Architect)  
**Project:** EDITH (Enhanced Distributed Intelligent Task Handler)  
**Date:** September 20, 2026  
**Status:** ARCHITECTURE REVIEW REPORT  

---

## 1. Executive Summary

This architecture review evaluates the current implementation state of the EDITH repository (`https://github.com/Prempujara/edith`) against the approved system specifications.

The goal of this review is to identify architectural deviations, missing boundaries, missing agent contracts, and security/design risks in existing backend and frontend implementations, and to provide actionable recommendations for the responsible team members (**Prem - Backend/Vertical Slice**, **Deev - Frontend**).

---

## 2. Architecture Review Findings Matrix

| Finding ID | Severity | Component | Target File(s) | Expected Architecture | Actual Implementation | Risk & Impact | Recommended Correction |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **AR-001** | `HIGH` | Agent Tier | `apps/backend/agents/` | Explicit module separation for the three agents (**JARVIS**, **EDITH**, **FRIDAY**) with dedicated prompts and tool boundaries. | `apps/backend/agents/__init__.py` is currently an empty placeholder file (0 bytes). Agent domain modules do not exist on `main`. | Developers may create a single monolithic AI handler instead of 3 domain-specialized agents. | **For Prem:** Create `jarvis_agent.py`, `edith_agent.py`, and `friday_agent.py` under `apps/backend/agents/` with clear domain prompts and tool permissions. |
| **AR-002** | `HIGH` | Runtime | `apps/backend/runtime/` | Shared Runtime providing `TaskTracker`, `EventBus`, `ToolRegistry`, and `DelegationManager`. Agents make delegation decisions. | `apps/backend/runtime/__init__.py` contains architecture docstring but missing concrete runtime class implementations on `main`. | Delayed integration of task tracking, child task creation, and event emission. | **For Prem:** Implement concrete `TaskTracker` and `DelegationManager` in `apps/backend/runtime/`. |
| **AR-003** | `MEDIUM` | API Gateway | `apps/backend/app/main.py` | FastAPI endpoints for task creation (`POST /api/v1/tasks`), status polling (`GET /api/v1/tasks/{id}`), and agent delegation state. | `apps/backend/app/main.py` only implements root `/` and `/health` endpoints. Task endpoints missing on `main`. | Frontend cannot submit or poll real tasks until task endpoints are exposed. | **For Prem:** Add task creation and polling endpoints in `apps/backend/api/router.py` conforming to `docs/architecture/communication.md`. |
| **AR-004** | `MEDIUM` | Frontend API Client | `apps/frontend/` | Next.js API client configured for backend task submission, status polling, and agent activity rendering. | Frontend contains Next.js boilerplate with initial page composition. Backend client integration is in feature branch (`feature/deev/frontend`). | Frontend may hardcode mock state rather than connecting to FastAPI contract. | **For Deev:** Connect Next.js fetch client to `http://localhost:8000/api/v1/tasks` with short polling per ADR-002. |
| **AR-005** | `LOW` | Secrets Handling | `.env.example` | `.env.example` template for API keys (`SLACK_WEBHOOK_URL`, `GEMINI_API_KEY`) with local `.env` excluded in `.gitignore`. | `.gitignore` exists and excludes `.env`. `.env.example` is missing in repository root. | New developers may hardcode secret strings directly in python files. | **For Team:** Add `.env.example` file in repository root with dummy placeholder values. |
| **AR-006** | `INFO` | Voice Adapter | `packages/voice` | Provider-independent voice adapter in `packages/voice` wrapping browser `SpeechRecognition` / `SpeechSynthesis`. | Client-side voice testing in progress on Deev's feature branch (`feature/deev/frontend-voice-testing`). | Minor code duplication if voice logic is embedded directly in page components. | **For Deev:** Extract voice logic into a reusable custom hook/adapter module conforming to `docs/architecture/voice-architecture.md`. |

---

## 3. Architectural Guidance for Developers

### Guidance for Prem (Backend / Runtime Lead)
1. Ensure the runtime does NOT attempt to hardcode AI agent selection logic. Pass raw prompts to JARVIS, and allow JARVIS to invoke delegation tools to trigger EDITH or FRIDAY.
2. Implement in-memory task tracking using thread-safe data structures (`asyncio.Lock` or dictionary stores) behind a repository interface per ADR-005.

### Guidance for Deev (Frontend Lead)
1. Implement configurable polling interval (default: 1500ms) when active task state is `RUNNING` or `DELEGATED`.
2. Ensure voice input uses soft fallback: if `window.SpeechRecognition` is undefined, keep standard text input operational without throwing console errors.
