# ADR-004 — Coding Agent and Tool Execution Sandboxing Boundary

**Author:** Mannan Shah (System Designer & Solutions Architect)  
**Date:** August 30, 2026  
**Status:** PROPOSED — REQUIRES TEAM APPROVAL  

---

## 1. Context
The Coding Agent formulates software modifications and requests filesystem operations or command executions. Allowing AI agents to execute arbitrary commands on the host machine without boundary controls introduces security risks (accidental system file modification, command injection, path traversal).

---

## 2. Decision
We establish a **Controlled Tool / Repository Execution Boundary (`apps/backend/tools`)**. The `CodingAgent` is prohibited from calling host system utilities directly; all filesystem reads/writes, git commands, and shell executions MUST be dispatched through validated Tool Layer functions enforcing path restrictions, allowed operations, and timeouts.

---

## 3. Rationale
1. **Security & Workspace Safety:** The Tool Execution Boundary enforces strict workspace checks (`path.resolve().startswith(workspace_root)`), blocking path traversal attempts (`../../`).
2. **Execution Timeouts:** Enforces maximum execution timeouts on shell executions (such as `pytest`), preventing frozen agent loops.
3. **Auditability & Observability:** Captures tool command arguments, stdout, stderr, and exit codes to emit events for dashboard log rendering.

---

## 4. Consequences
* **Positive:** Safe code execution, zero risk of host OS damage during college demos, clear command telemetry.
* **Negative:** Agent actions are strictly constrained to permitted tool definitions.
