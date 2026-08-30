# ADR-001 — Architecture Style Selection: Modular Monolith

**Author:** Mannan Shah (System Designer & Solutions Architect)  
**Date:** August 30, 2026  
**Status:** PROPOSED — REQUIRES TEAM APPROVAL  

---

## 1. Context
EDITH is a multi-agent AI task-handling platform built as a college Software Project Management (SPM) project. The project operates under a strict **₹0 budget**, single-sprint development cycles, and a team of 4 developers. We must select an architectural style that maximizes maintainability and code structure while minimizing operational complexity, deployment cost, and latency.

---

## 2. Decision
We adopt a **Modular Monolith** architecture pattern hosted within a single FastAPI Python backend (`apps/backend`) and Next.js frontend (`apps/frontend`). Core subsystems (Orchestrator, Coding Agent, Tool Execution Layer, Voice, Slack) are organized into strictly isolated packages (`packages/*`) with clean in-memory interfaces.

---

## 3. Rationale
1. **Low Operational Overhead:** Eliminates the need to configure, manage, and debug distributed service networking, service discovery, or container orchestration (Kubernetes/Docker Swarm).
2. **Zero Financial Cost:** Runs completely within a single free local Python process without requiring paid cloud hosting or multi-node infrastructure.
3. **High Development Velocity:** Allows the team of 4 developers to work in a unified monorepo with fast local feedback loops (`uvicorn` hot reloading).
4. **Enforced Modularity:** Package-based code isolation ensures clean boundaries, enabling individual modules to be extracted into independent microservices in the future if scale demands it.

---

## 4. Alternatives Considered
* **Traditional Monolith (Unstructured):** Easy to start, but risks turning into an unstructured codebase where Orchestrator, UI, and low-level tools become tightly coupled.
* **Microservices Architecture:** Over-engineered for a college MVP. Introduces network latency, RPC/gRPC overhead, complex distributed tracing, and container deployment headaches without providing value for a local project demo.

---

## 5. Consequences
* **Positive:** Fast development, zero deployment cost, simple debugging, clean package separation.
* **Negative:** All backend components share the same Python runtime process; a critical process crash impacts the entire backend (mitigated by asyncio exception handling).

---

## 6. MVP Impact & Future Considerations
* **MVP Impact:** Guarantees successful delivery within Sprint 1/2 timelines under ₹0 budget.
* **Future Considerations:** If concurrent workload scales post-college, isolated packages (`packages/agents`, `packages/slack`) can be extracted into standalone microservices.
