# EDITH-001 — Tool Architecture & Permission Sandboxing Boundary

**Author:** Mannan Shah (System Designer & Solutions Architect)  
**Project:** EDITH (Enhanced Distributed Intelligent Task Handler)  
**Date:** September 20, 2026  
**Status:** APPROVED ARCHITECTURE BASELINE  

---

## 1. Tool Layer Vision & Boundaries

AI agents formulate edit strategies and automation commands. Allowing raw agents to execute unvalidated system commands directly on the host machine poses severe security risks (accidental system file deletion, arbitrary code execution, token leakage).

The **Tool Layer Boundary (`apps/backend/tools` / `packages/tools`)** serves as a strict gateway between agents and the host environment.

```
┌─────────────────────────────────────────────────────────────┐
│                   AGENT TOOL REQUEST                        │
│            "file_write" / "shell_execute"                   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    TOOL REGISTRY & SAFETY                   │
│  1. Check Tool Registration & Domain Ownership              │
│  2. Evaluate Permission Level (Safe / Sensitive / Confirm)  │
│  3. Validate Workspace Bounds (path.resolve())              │
│  4. Enforce Timeout Limits                                  │
└──────────────────────────────┬──────────────────────────────┘
                               │
           ┌───────────────────┴───────────────────┐
           │ Allowed / Approved                    │ Denied / Violation
           ▼                                       ▼
┌──────────────────────────────┐        ┌──────────────────────────────┐
│  TOOL EXECUTION SANDBOX      │        │  RAISE ToolPermissionError   │
│  • Reads / Writes Files      │        │  Return Error to Agent       │
│  • Runs Guarded Subprocess   │        └──────────────────────────────┘
└──────────────────────────────┘
```

---

## 2. Tool Classification & Permission Matrix

Tools are registered with explicit permission metadata:

| Permission Level | Description | Example Tools | User Confirmation Required? |
| :--- | :--- | :--- | :--- |
| **SAFE** | Read-only operations that do not mutate disk, state, or external networks. | `file_read`, `directory_list`, `git_status`, `web_search` | No — Automated execution. |
| **SENSITIVE** | Write operations confined strictly within the project workspace bounds. | `file_write`, `file_move`, `git_commit` | No — Subject to workspace path lock. |
| **CONFIRMATION_REQUIRED** | Operations with system impact or high risk of unintended state change. | `shell_execute` (custom scripts), `desktop_click`, `git_push` | Yes — Requires user confirmation in Dashboard. |
| **FORBIDDEN** | High-risk operations prohibited in the local environment. | `rm -rf /`, raw disk formatting, modifying system environment files outside workspace. | Strictly Prohibited. |

---

## 3. Tool Sandboxing & Execution Safeguards

### 3.1 Workspace Path Lock
All filesystem tools enforce strict path resolution:
```python
# Conceptual Path Boundary Checker
def validate_workspace_path(target_path: str, workspace_root: str) -> bool:
    resolved_target = Path(target_path).resolve()
    resolved_root = Path(workspace_root).resolve()
    if not resolved_target.is_relative_to(resolved_root):
        raise PermissionError(f"Access denied: Path '{target_path}' is outside workspace root.")
    return True
```

### 3.2 Command Execution Timeouts
Shell execution tools (`subprocess`) wrap commands with mandatory execution timeouts (e.g. `timeout=30s`). If a command freezes, the tool sandbox terminates the process tree cleanly and returns a structured error to the agent.

### 3.3 Output Sanitization & Truncation
Tool outputs returned to AI prompts are sanitized to strip ANSI color codes, environment secret strings, and truncated if stdout exceeds maximum token budgets (e.g., max 4000 characters).

---

## 4. Tool Registry Metadata Schema

Tools register capability schemas in the Shared Runtime Tool Registry:

```json
{
  "name": "file_write",
  "domain": "FILESYSTEM",
  "owning_agent": "FRIDAY",
  "permission_level": "SENSITIVE",
  "description": "Writes content to a file inside the project workspace.",
  "parameters": {
    "file_path": { "type": "string", "required": true },
    "content": { "type": "string", "required": true },
    "overwrite": { "type": "boolean", "default": false }
  },
  "execution_environment": "LOCAL"
}
```
