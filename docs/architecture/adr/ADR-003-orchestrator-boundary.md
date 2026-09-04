# ADR-003 — Orchestrator Responsibilities and Boundaries

**Author:** Mannan Shah (System Designer & Solutions Architect)  
**Date:** August 30, 2026  
**Status:** PROPOSED — REQUIRES TEAM APPROVAL  

---

## 1. Context
In multi-agent task handling systems, workflow coordinators frequently risk becoming "God Objects" that absorb UI rendering, API formatting, direct filesystem manipulation, integration logic, and vendor SDK calls. We must strictly define the boundaries of the EDITH Orchestrator.

---

## 2. Decision
The Orchestrator shall strictly own **Task Execution Request Interpretation, Workflow Routing, Agent Selection, Execution Coordination, Tool Request Coordination, Logical Task Tracking, Result Processing, and Event Emission**. It is explicitly forbidden from performing low-level tool execution, direct LLM prompt formatting, UI rendering, Voice provider logic, Slack HTTP messaging, database queries, or vendor AI SDK integrations.

---

## 3. Rationale
1. **Single Responsibility Principle (SRP):** Keeps the core decision engine clean, testable, and isolated from external changes.
2. **Component Decoupling:** Changes to Slack webhooks, Voice libraries, or low-level tool commands will never break the Orchestrator's core state machine logic.
3. **Testability:** The Orchestrator can be unit-tested using mock agents and mock task state stores without instantiating web servers or external APIs.

---

## 4. Anti-Patterns Explicitly Prohibited
* Direct filesystem calls (`open()`, `subprocess.run()`) inside Orchestrator code.
* Direct HTTP calls to Slack or external cloud APIs inside Orchestrator code.
* Direct construction of React/JSX or HTML strings inside Orchestrator code.
* Direct coupling to vendor-specific AI provider SDKs inside Orchestrator code.

---

## 5. Consequences
* **Positive:** Clear architectural boundaries, robust testing, maintainable state machine.
* **Negative:** Requires strict discipline and intermediate event subscribers / adapters for external notifications.
