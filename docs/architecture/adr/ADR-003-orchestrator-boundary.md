# ADR-003 — Orchestrator Responsibilities and Boundaries

**Author:** Mannan Shah (System Designer & Solutions Architect)  
**Date:** August 30, 2026  
**Status:** PROPOSED — REQUIRES TEAM APPROVAL  

---

## 1. Context
In multi-agent task handling systems, workflow coordinators frequently risk becoming "God Objects" that absorb UI rendering, API formatting, direct filesystem manipulation, and integration logic. We must strictly define the boundaries of the EDITH Orchestrator.

---

## 2. Decision
The Orchestrator shall strictly own **Task Lifecycle Management, Agent Dispatching, Top-Level Error Handling, and Event Emission**. It is explicitly forbidden from performing low-level tool execution, direct LLM prompt formatting, UI rendering, Voice processing, or Slack HTTP messaging.

---

## 3. Reason
1. **Single Responsibility Principle (SRP):** Keeps the core decision engine clean, testable, and isolated from external changes.
2. **Component Decoupling:** Changes to Slack webhooks, Voice libraries, or low-level tool commands will never break the Orchestrator's core state machine logic.
3. **Testability:** The Orchestrator can be unit-tested using mock agents and mock task stores without instantiating web servers or external APIs.

---

## 4. Anti-Patterns Explicitly Prohibited
* Direct filesystem calls (`open()`, `subprocess.run()`) inside Orchestrator code.
* Direct HTTP calls to Slack or external cloud APIs inside Orchestrator code.
* Direct construction of React/JSX or HTML strings.

---

## 5. Consequences
* **Positive:** Clear architectural boundaries, robust testing, maintainable state machine.
* **Negative:** Requires strict discipline and intermediate event subscribers / adapters for external notifications.
