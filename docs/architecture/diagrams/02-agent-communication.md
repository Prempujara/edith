# Architecture Diagram 02 — Agent Communication & Delegation Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant JARVIS as JARVIS (Primary Agent)
    participant Runtime as Shared Runtime Infrastructure
    participant EDITH as EDITH (Computer Agent)
    participant FRIDAY as FRIDAY (File Agent)
    participant Tool as Tool Execution Sandbox

    User->>JARVIS: Prompt: "Organize docs/ and capture browser screenshot"
    Note over JARVIS: Analyzes task requirements.<br/>Decides subtasks are required.

    JARVIS->>Runtime: Delegate Subtask 1 (target: FRIDAY, task: Organize docs/)
    Runtime->>FRIDAY: Dispatch Child Task 1
    FRIDAY->>Tool: Execute file_move / file_write
    Tool-->>FRIDAY: File execution output
    FRIDAY-->>Runtime: Return Subtask 1 Result
    Runtime-->>JARVIS: Subtask 1 Complete Notification

    JARVIS->>Runtime: Delegate Subtask 2 (target: EDITH, task: Browser Screenshot)
    Runtime->>EDITH: Dispatch Child Task 2
    EDITH->>Tool: Execute browser_open / desktop_screenshot
    Tool-->>EDITH: Screenshot image artifact
    EDITH-->>Runtime: Return Subtask 2 Result
    Runtime-->>JARVIS: Subtask 2 Complete Notification

    Note over JARVIS: Aggregates subtask outputs.<br/>Formulates final user response.
    JARVIS->>User: Return final summary and screenshots
```

### Delegation Rules
1. **Agent Autonomy:** JARVIS inspects task complexity and delegates specific domain subtasks.
2. **Runtime Transport:** The Shared Runtime routes subtasks, generates child task IDs, and tracks progress.
3. **Execution Sandboxing:** Subtask actions execute through guarded Tool Sandbox endpoints.
