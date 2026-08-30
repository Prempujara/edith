# ADR-005 — Persistence Strategy: In-Memory Task Storage for MVP

**Author:** Mannan Shah (System Designer & Solutions Architect)  
**Date:** August 30, 2026  
**Status:** PROPOSED — REQUIRES TEAM APPROVAL  

---

## 1. Context
EDITH requires state tracking for active tasks, execution steps, logs, and final results. We must decide whether to deploy a database (PostgreSQL, SQLite, MongoDB) or use an in-memory task repository for the MVP release under **Rule 4 (Zero-Budget)**.

---

## 2. Decision
We adopt an **In-Memory Task Repository (`TaskStore`)** backed by Python thread-safe dictionary structures, hidden behind an abstract interface (`ITaskRepository`).

---

## 3. Reason
1. **Zero Infrastructure Overhead:** Eliminates the need to install, configure, migrate, or run database engines (PostgreSQL/Docker) during local setup and college presentations.
2. **Speed & Simplicity:** Zero database network latency; instant state updates for short polling queries.
3. **Repository Pattern Protection:** Wrapping `TaskStore` in `ITaskRepository` allows a SQL database (SQLite/PostgreSQL) to be plugged in during post-MVP sprints without refactoring business logic.

---

## 4. Consequences & Limitations
* **Positive:** Instant startup, zero database dependencies, zero configuration cost.
* **Negative:** Task history is volatile and resets if the backend Python server is restarted (fully acceptable for live college MVP demonstrations).
