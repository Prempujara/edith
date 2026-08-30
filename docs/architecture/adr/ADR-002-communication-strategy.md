# ADR-002 — Realtime Communication Strategy: Configurable Short HTTP Polling

**Author:** Mannan Shah (System Designer & Solutions Architect)  
**Date:** August 30, 2026  
**Status:** PROPOSED — REQUIRES TEAM APPROVAL  

---

## 1. Context
The Next.js dashboard needs to display live task progress, agent step updates, terminal execution logs, and completion status. We must decide on a communication mechanism between the Next.js frontend and FastAPI backend for dashboard updates.

---

## 2. Decision
We adopt **Configurable Short HTTP Polling (`PROPOSED: GET /api/v1/tasks/{task_id}`)** during active task states (`QUEUED`, `IN_PROGRESS` — *PROPOSED STATES*) for the MVP release.

---

## 3. Rationale
1. **Implementation Simplicity:** Standard REST `GET` requests require zero socket connection state management, reconnection logic, or custom WebSocket framing protocols.
2. **Zero Budget & Infrastructure Friction:** Polling works out-of-the-box in all browser environments and local development proxies without requiring persistent socket infrastructure.
3. **Low Load Profile:** In a college MVP setting with small-team task executions, periodic HTTP polling incurs near-zero CPU and memory footprint on FastAPI.
4. **Resilience:** Unaffected by transient network drops or proxy socket drops that typically disconnect WebSockets.

---

## 4. Alternatives Considered
* **WebSockets (WS/WSS):** Provides true bi-directional streaming, but introduces connection state handling, ping/pong heartbeats, reconnection hooks in React, and extra complexity.
* **Server-Sent Events (SSE):** Simpler than WebSockets for uni-directional streaming, but still requires persistent HTTP connection handling and custom client event streams.

---

## 5. Consequences
* **Positive:** Reduced codebase complexity, 100% reliable local development, easy inspection in browser DevTools.
* **Negative:** Slight latency delay before task updates reflect in UI (fully acceptable for MVP task execution timelines).

---

## 6. MVP Impact & Future Considerations
* **MVP Impact:** Fast implementation in Sprint 2 without WebSocket bugs.
* **Future Considerations:** The API event system can be exposed via WebSockets or SSE in post-MVP sprints if sub-second UI log streaming becomes a requirement.
