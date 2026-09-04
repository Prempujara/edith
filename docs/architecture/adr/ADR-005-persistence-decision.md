# ADR-005 — Persistence Strategy: In-Memory Task Storage for MVP

**Author:** Mannan Shah (System Designer & Solutions Architect)  
**Date:** August 30, 2026  
**Status:** PROPOSED — REQUIRES TEAM APPROVAL  

---

## 1. Context
EDITH requires state tracking for active tasks, execution steps, logs, and final results. We must decide whether to deploy a database (PostgreSQL, SQLite, MongoDB) or use an in-memory task repository for the MVP release under **Rule 4 (Zero-Budget)**.

---

## 2. Decision
We adopt **In-Memory Task State Storage** for the MVP, operating behind a replaceable persistence/repository boundary.

---

## 3. Rationale
1. **Zero Infrastructure Overhead:** Eliminates the need to install, configure, migrate, or run database engines (PostgreSQL/Docker) during local setup and college presentations.
2. **Speed & Simplicity:** Zero database network latency; instant state updates for periodic HTTP polling queries.
3. **Repository Pattern Protection:** Accessing task state through a persistence abstraction layer allows a SQL database (SQLite/PostgreSQL) to be plugged in during post-MVP sprints without refactoring business logic.

---

## 4. Consequences & Limitations
* **Positive:** Instant startup, zero database dependencies, zero configuration cost.
* **Negative:** Task history is volatile and resets if the backend Python server is restarted (fully acceptable for live college MVP demonstrations).
