# ADR-004 — Coding Agent and Tool Execution Sandboxing Boundary

**Author:** Mannan Shah (System Designer & Solutions Architect)  
**Date:** August 30, 2026  
**Status:** PROPOSED — REQUIRES TEAM APPROVAL  

---

## 1. Context
The Coding Agent formulates software modifications and requests filesystem operations or command executions. Allowing AI agents to execute arbitrary commands on the host machine without sandboxing introduces severe security risks (accidental system file modification, command injection, path traversal).

---

## 2. Decision
We establish a mandatory **Tool Execution Sandbox Layer (`apps/backend/tools`)**. The `CodingAgent` is prohibited from calling host system utilities directly; all filesystem reads/writes, git commands, and shell executions MUST be dispatched through validated Tool Layer functions.

---

## 3. Reason
1. **Security & Workspace Safety:** The Tool Sandbox enforces strict workspace boundary checks (`path.resolve().startswith(workspace_root)`), blocking path traversal attacks (`../../`).
2. **Execution Timeouts:** Enforces maximum execution timeouts (e.g., 60 seconds) on shell executions (such as `pytest`), preventing frozen agent loops.
3. **Auditability & Observability:** Captures every tool command argument, stdout, stderr, and exit code to emit `tool.executed` events for dashboard terminal rendering.

---

## 4. Consequences
* **Positive:** Safe code execution, zero risk of host OS damage during college demos, clear command telemetry.
* **Negative:** Agent actions are strictly constrained to permitted tool definitions.
