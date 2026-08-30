# ADR-002 — Realtime Communication Strategy: Short HTTP Polling

**Author:** Mannan Shah (System Designer & Solutions Architect)  
**Date:** August 30, 2026  
**Status:** PROPOSED — REQUIRES TEAM APPROVAL  

---

## 1. Context
The Next.js dashboard needs to display live task progress, agent step updates, terminal execution logs, and completion status. We must decide on a communication mechanism between the Next.js frontend and FastAPI backend for real-time dashboard updates.

---

## 2. Decision
We adopt **Short HTTP Polling (`GET /api/v1/tasks/{task_id}`) at a 2-second interval** during active task states (`QUEUED`, `IN_PROGRESS`) for the MVP release.

---

## 3. Reason
1. **Implementation Simplicity:** Standard REST `GET` requests require zero socket connection state management, reconnection logic, or custom WebSocket framing protocols.
2. **Zero Budget & Infrastructure Friction:** Polling works out-of-the-box in all browser environments and local development proxies without requiring persistent socket infrastructure.
3. **Low Load Profile:** In a college MVP setting with 1–5 concurrent task executions, a 2-second HTTP polling request incurs near-zero CPU and memory footprint on FastAPI.
4. **Resilience:** Unaffected by transient network drops or proxy socket drops that typically disconnect WebSockets.

---

## 4. Alternatives Considered
* **WebSockets (WS/WSS):** Provides true bi-directional streaming, but introduces connection state handling, ping/pong heartbeats, reconnection hooks in React, and extra complexity.
* **Server-Sent Events (SSE):** Simpler than WebSockets for uni-directional streaming, but still requires persistent HTTP connection handling and custom client event streams.

---

## 5. Consequences
* **Positive:** Reduced codebase complexity, 100% reliable local development, easy inspection in browser DevTools.
* **Negative:** Up to 2-second latency delay before task updates reflect in UI (acceptable for MVP task execution timelines).

---

## 6. MVP Impact & Future Considerations
* **MVP Impact:** Fast implementation in Sprint 2 without WebSocket bugs.
* **Future Considerations:** The API event bus can be exposed via WebSockets or SSE in post-MVP sprints if sub-second UI log streaming becomes a hard requirement.
