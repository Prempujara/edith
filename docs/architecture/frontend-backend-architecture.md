# EDITH-001 — Frontend & Backend Architecture

**Author:** Mannan Shah (System Designer & Solutions Architect)  
**Project:** EDITH (Enhanced Distributed Intelligent Task Handler)  
**Date:** August 30, 2026  
**Status:** Complete / Proposed Blueprint  

---

## 1. Overview

This document specifies the communication contract, responsibilities, CORS security policy, and realtime update strategy between the EDITH Next.js Frontend (`apps/frontend`) and the FastAPI Backend (`apps/backend`).

---

## 2. Division of Responsibilities

```mermaid
graph LR
    subgraph Frontend [Next.js Web UI - Client Side]
        A[User Input Form] --> B[STT Voice Capture]
        B --> C[API HTTP Client]
        C --> D[Task Polling Loop]
        D --> E[Log & Diff Renderer]
        E --> F[TTS Audio Trigger]
    end

    subgraph Communication [REST HTTP Interface]
        C <-->|POST /api/v1/tasks| G[FastAPI Router]
        D <-->|GET /api/v1/tasks/{id}| G
    end

    subgraph Backend [FastAPI Application - Server Side]
        G --> H[Pydantic Validation]
        H --> I[TaskStore Repository]
        I --> J[Orchestrator Engine]
        J --> K[Coding Agent]
        K --> L[Tool Sandbox Execution]
    end
```

### 2.1 Frontend Responsibilities
* **User Input Ingestion:** Provides text area and microphone recording button for task command entry.
* **Client-Side Speech Ingestion (STT):** Uses browser-native Web Speech API (`SpeechRecognition`) to transcribe spoken user commands locally without server-side processing cost.
* **HTTP Communication:** Formats task requests and handles asynchronous HTTP responses cleanly using `fetch` or `axios`.
* **State & Status Polling:** Executes a 2-second short polling interval while a task is active (`QUEUED` or `IN_PROGRESS`) to refresh status and progress telemetry.
* **Visual Rendering:** Displays real-time task progress step-by-step, code diffs, terminal execution logs, and completion status badges.
* **Client-Side Speech Output (TTS):** Speaks execution summaries upon completion using browser-native `SpeechSynthesis`.

### 2.2 Backend Responsibilities
* **API Entrypoint & Routing:** Exposes RESTful HTTP endpoints under `/api/v1/` `[PROPOSED]`.
* **Request Validation & Security:** Enforces strict Pydantic payload models and CORS origin checks.
* **Task State Management:** Manages task lifecycle transitions safely inside the in-memory `TaskStore`.
* **Execution & Orchestration:** Orchestrates LLM prompt execution, context retrieval, tool invocation, and error handling.
* **Telemetry & Event Publishing:** Captures execution logs, tool stdout/stderr, and domain events for API query consumption.

---

## 3. Realtime Strategy Decision: HTTP Polling vs. WebSockets

### 3.1 Architectural Comparison

| Dimension | Option A: WebSockets (WS/WSS) | Option B: Short HTTP Polling (Chosen MVP Strategy) |
| :--- | :--- | :--- |
| **Complexity** | High (Requires connection lifecycle, reconnection, ping/pong, socket state management) | **Very Low** (Standard stateless HTTP `GET` requests) |
| **Server Overhead** | High persistent memory footprint per open socket | **Negligible** for single-user/small-team MVP |
| **Browser Compatibility**| Requires fallback logic | **100% Native support** in every environment |
| **Debuggability** | Requires WS framing tools | **Standard Network Tab** in browser dev tools |
| **₹0 Budget Fit** | Requires persistent socket infrastructure | **Ideal** — Zero special server/proxy requirements |

### 3.2 Decision & Justification
**Selected Strategy:** **Short HTTP Polling (`GET /api/v1/tasks/{task_id}`) every 2000ms.**

For a college SPM project MVP with 1–5 concurrent tasks, short polling provides an identical perceived user experience to WebSockets while eliminating WebSocket connection state management, firewall socket drops, and complex server-side socket routing code.

---

## 4. CORS (Cross-Origin Resource Sharing) Specification

To enable seamless communication during local development (where Next.js runs on port `3000` and FastAPI runs on port `8000`), the backend must configure FastAPI `CORSMiddleware`.

### 4.1 Development CORS Policy Configuration
```python
# Proposed Backend FastAPI CORS Setup (apps/backend/main.py)
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)
```

---

## 5. API Endpoints Contract Matrix [PROPOSED]

| Method | Path | Request Payload | Expected Response | Description |
| :--- | :--- | :--- | :--- | :--- |
| **GET** | `/health` | None | `200 OK {"status": "healthy"}` | Server health verification |
| **POST** | `/api/v1/tasks` `[PROPOSED]` | `{"prompt": string}` | `202 Accepted {"task_id": string, "status": string}` | Create & enqueue new task |
| **GET** | `/api/v1/tasks/{task_id}` `[PROPOSED]` | None | `200 OK {"task_id": string, "status": string, "result": object, "logs": array}` | Fetch task status & logs |
| **GET** | `/api/v1/tasks` `[PROPOSED]` | None | `200 OK [{"task_id": string, "status": string}]` | List recent tasks |
