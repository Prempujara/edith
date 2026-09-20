# Architecture Diagram 03 — Task Lifecycle State Machine

```mermaid
stateDiagram-v2
    [*] --> PENDING: Client Submits Task
    
    PENDING --> ASSIGNED: Shared Runtime Assigns Agent
    
    state ASSIGNED {
        [*] --> RUNNING: Agent Starts Execution Loop
    }
    
    state RUNNING {
        [*] --> THINKING: Agent Formulates Action
        THINKING --> WAITING_FOR_TOOL: Tool Request Dispatched
        WAITING_FOR_TOOL --> THINKING: Tool Result Returned
        
        THINKING --> DELEGATED: Agent Delegates Subtask
        DELEGATED --> THINKING: Subtask Complete Notification
    }
    
    RUNNING --> COMPLETED: Agent Emits Final Result
    RUNNING --> FAILED: Exception / Unrecoverable Error
    RUNNING --> TIMED_OUT: Watchdog Exceeds Max Execution Limit
    
    PENDING --> CANCELLED: Aborted by User
    RUNNING --> CANCELLED: Aborted by User
    DELEGATED --> CANCELLED: Parent Task Aborted
    
    COMPLETED --> [*]
    FAILED --> [*]
    TIMED_OUT --> [*]
    CANCELLED --> [*]
```

### Lifecycle Highlights
- **Parent-Child Linkage:** Delegated tasks maintain `parent_task_id` linkage.
- **Cascading Cancellation:** Aborting a parent task automatically cancels all active delegated child subtasks.
- **Deterministic State Tracking:** State transitions emit async domain events to the Web Dashboard.
