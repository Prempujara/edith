# Architecture Diagram 05 — Tool Permission & Sandboxing Pipeline

```mermaid
flowchart TD
    Start([Agent Formulates Tool Request]) --> RegistryLookup{Is Tool Registered in Registry?}
    
    RegistryLookup -- No --> Deny1[Reject: ToolNotFoundError]
    RegistryLookup -- Yes --> CheckPerm{Check Permission Level}

    CheckPerm -- FORBIDDEN --> Deny2[Reject: ForbiddenOperationError]
    CheckPerm -- SAFE --> CheckPath
    CheckPerm -- SENSITIVE --> CheckPath
    CheckPerm -- CONFIRMATION_REQUIRED --> ConfirmStep{User Confirmed in UI?}

    ConfirmStep -- No / Timed Out --> Deny3[Reject: UserConfirmationDenied]
    ConfirmStep -- Yes --> CheckPath

    CheckPath{Is File Path inside Workspace Root?} -- No --> Deny4[Reject: PathTraversalViolation]
    CheckPath -- Yes --> Exec[Execute Tool in Subprocess / Sandbox with Timeout]

    Exec --> ExecCheck{Execution Successful?}
    ExecCheck -- Timeout / Exception --> FailOut[Return Error Payload to Agent]
    ExecCheck -- Success --> Sanitize[Sanitize Output & Truncate]
    Sanitize --> SuccessOut[Return Tool Output Result to Agent Context]
```

### Permission Levels
- **SAFE:** Auto-approved (Read-only).
- **SENSITIVE:** Auto-approved within workspace bounds.
- **CONFIRMATION_REQUIRED:** Suspends execution until user approves via UI.
- **FORBIDDEN:** Blocked outright.
