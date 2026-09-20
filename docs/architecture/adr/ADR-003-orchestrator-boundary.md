# ADR-003 — Agent Delegation and Shared Runtime Boundaries

**Author:** Mannan Shah (System Designer & Solutions Architect)  
**Date:** August 30, 2026 (Updated: September 20, 2026)  
**Status:** ACCEPTED — REVISED FOR MULTI-AGENT DELEGATION  

---

## 1. Context
In multi-agent task handling systems, workflow coordinators frequently risk becoming central "God Objects" or single centralized AI decision-makers that attempt to perform reasoning, intent classification, agent selection, UI rendering, tool execution, and integration routing.

We must strictly define the boundary between **Specialized Agents (JARVIS, EDITH, FRIDAY)** and the **Shared Runtime / Orchestration Infrastructure**.

---

## 2. Decision
1. **Agents Make Delegation Decisions:** The specialized agents themselves (JARVIS as primary, EDITH as computer specialist, FRIDAY as file specialist) inspect task context and decide **if delegation is required** and **which specialized agent should receive the task**.
2. **Shared Runtime Coordinates Execution:** The Shared Runtime (orchestration infrastructure) strictly owns **Execution Coordination, Message Transport, Routing Infrastructure, Task State Tracking, Tool Registry Access, Result Delivery, and Failure Propagation**.
3. **Runtime Prohibition:** The Shared Runtime is explicitly forbidden from acting as a central AI reasoning engine, hardcoding LLM prompt logic, performing low-level tool execution directly, or silently overriding agent delegation decisions.

```
┌─────────────────────────────────────────────────────────────┐
│                           AGENTS                            │
│  • Reasoning & Intent Analysis                              │
│  • Decides WHEN delegation is needed                        │
│  • Decides WHICH agent (JARVIS / EDITH / FRIDAY) receives it│
└──────────────┬──────────────────────────────┬───────────────┘
               │ Task / Delegation Request   │ Results / Errors
               ▼                              ▲
┌─────────────────────────────────────────────────────────────┐
│                       SHARED RUNTIME                        │
│  • Execution Coordination & Routing                         │
│  • Message Transport & Event Emission                       │
│  • Task Lifecycle & Parent/Child State Tracking             │
│  • Tool Registry Access & Permission Checks                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Rationale
1. **Agent Autonomy & Specialization:** JARVIS, EDITH, and FRIDAY are specialized domain experts. JARVIS knows when a computer-control task requires EDITH or a document filing task requires FRIDAY.
2. **Decoupled Infrastructure:** The Shared Runtime remains a lean, deterministic, highly-testable execution framework independent of LLM model changes or prompt engineering.
3. **Single Responsibility Principle (SRP):** Reasoning belongs in the agent prompt and model execution layer; state machine mechanics, transport, and safety checks belong in the runtime layer.

---

## 4. Anti-Patterns Explicitly Prohibited
* Hardcoding central AI intent routing logic inside the runtime state machine.
* Direct filesystem calls (`open()`, `subprocess.run()`) inside runtime orchestration code without passing through validated tool boundaries.
* Direct HTTP calls to Slack or external cloud APIs inside core agent decision loops.
* Silent execution of cross-agent delegation without parent-child task tracking.

---

## 5. Consequences
* **Positive:** Autonomous agent delegation, clean separation between reasoning and infrastructure transport, high testability, scalable multi-agent coordination.
* **Negative:** Requires structured task delegation contracts (`source_agent`, `target_agent`, `parent_task_id`) passed via Shared Runtime messaging.

