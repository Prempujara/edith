# EDITH-001 — Request & Execution Flow Specification

**Author:** Mannan Shah (System Designer & Solutions Architect)  
**Project:** EDITH (Enhanced Distributed Intelligent Task Handler)  
**Date:** August 30, 2026  
**Status:** Proposed Specification — Subject to EDITH-000 Approval  

---

## 1. Overview

This document defines the conceptual end-to-end request and execution flow for EDITH, covering every stage from user prompt ingestion to agent execution, dashboard status updates, voice output, and Slack notifications.

> **Contract Rule Disclaimer (Rule 8):** All request/response schemas, API endpoint paths, event names, and task lifecycle states referenced in this document are **PROPOSED — REQUIRES EDITH-000 APPROVAL** and subject to final contract verification upon approval of **EDITH-000 (Core Specification)**.

---

## 2. End-to-End Execution Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant VoiceSTT as Voice Input (STT)
    participant UI as Next.js Dashboard
    participant API as FastAPI Gateway
    participant Store as Task State Store
    participant Orch as Orchestrator
    participant Agent as Coding Agent
    participant Tool as Tool Execution Boundary
    participant EventBus as Internal Event System
    participant VoiceTTS as Voice Output (TTS)
    participant Slack as Slack Adapter

    %% Step 1: Command Ingestion
    alt Text Input Flow
        User->>UI: Types Task Prompt
    else Voice Input Flow
        User->>VoiceSTT: Speaks Task Prompt
        VoiceSTT->>UI: Transcribed Text String
    end

    %% Step 2: Task Submission
    UI->>API: Task Creation Request [PROPOSED: POST /api/v1/tasks]
    API->>Store: Create Task Record (status="CREATED" [PROPOSED])
    API-->>UI: 202 Accepted { "task_id": "uuid", "status": "CREATED" } [PROPOSED]

    %% Step 3: Orchestration Launch
    API->>Orch: Submit Task (task_id)
    Orch->>Store: Update Task Status ("QUEUED" [PROPOSED])
    Orch->>EventBus: Publish Task Queued Event [PROPOSED]

    %% Step 4: Agent Execution Loop
    Orch->>Store: Update Task Status ("IN_PROGRESS" [PROPOSED])
    Orch->>EventBus: Publish Task Started Event [PROPOSED]
    Orch->>Agent: Dispatch Task (prompt, context)

    loop Iterative Reasoning & Tool Execution
        Agent->>Tool: Request Action (e.g., READ_FILE, RUN_TEST)
        Tool->>Tool: Execute Validated Action in Workspace
        Tool-->>Agent: Action Output (stdout, stderr, exit code)
        Orch->>EventBus: Publish Tool Executed Event [PROPOSED]
    end

    Agent-->>Orch: Task Execution Summary / Completion Result

    %% Step 5: Finalization & Event Distribution
    alt Execution Successful
        Orch->>Store: Update Task Status ("COMPLETED" [PROPOSED])
        Orch->>EventBus: Publish Task Completion Event [PROPOSED]
    else Execution Failed / Error
        Orch->>Store: Update Task Status ("FAILED" [PROPOSED])
        Orch->>EventBus: Publish Task Failure Event [PROPOSED]
    end

    %% Step 6: Observer Notification Flows
    par Dashboard Status Update
        loop Periodic Polling (Configurable Interval)
            UI->>API: Task Status Query [PROPOSED: GET /api/v1/tasks/{id}]
            API-->>UI: 200 OK { status, logs, result } [PROPOSED]
            UI->>UI: Render Updated Status & Logs
        end
    and Voice Response
        EventBus->>VoiceTTS: Trigger Audio Summary
        VoiceTTS->>User: Spoken Response Summary
    and Slack Notification
        EventBus->>Slack: Trigger Slack Notification
        Slack->>Slack: HTTP Webhook Request to Channel
    end
```

---

## 3. Step-by-Step Execution Lifecycle Breakdown

### Stage 1: User Command Ingestion
* **Text Mode:** The user enters a natural language task description into the Next.js frontend form.
* **Voice Mode:** The user clicks the microphone button in the UI. The Speech-to-Text (STT) adapter captures audio input, transcribes it to a clean text string, and populates the text form.

### Stage 2: API Gateway & Task Creation
* The frontend issues a REST task creation request (`PROPOSED: POST /api/v1/tasks`).
* The FastAPI gateway validates the request payload against validation schemas.
* A unique task identifier is generated.
* An initial task record is saved to the task state store with status `CREATED` `[PROPOSED]`.
* The API immediately returns an HTTP 202 Accepted response containing `task_id` and initial status to the client, preventing HTTP request timeouts.

### Stage 3: Orchestrator Routing & Initialization
* The API hands over `task_id` to the Orchestrator via an internal async queue.
* Orchestrator updates task status to `QUEUED` `[PROPOSED]` and emits a Task Queued Event `[PROPOSED]`.
* Orchestrator inspects the task prompt, selects the target agent (`CodingAgent`), updates task status to `IN_PROGRESS` `[PROPOSED]`, and emits a Task Started Event `[PROPOSED]`.

### Stage 4: Agent Reasoning & Controlled Tool Execution
* The `CodingAgent` receives the prompt and builds initial workspace context by requesting tool reads.
* The `Tool Execution Boundary` validates that requested file paths reside inside the permitted workspace sandbox and executes the reads.
* The `CodingAgent` formulates execution steps (e.g., modifying code files, running tests).
* Each tool action output (stdout, stderr, exit code) is captured and recorded.
* Tool execution events `[PROPOSED]` are emitted for log tracking.

### Stage 5: Task Resolution & Lifecycle Termination
* Upon completing all planned sub-steps, the `CodingAgent` returns a structured summary to the Orchestrator.
* If execution succeeded without unhandled errors, Orchestrator marks task status as `COMPLETED` `[PROPOSED]` and emits a Task Completion Event `[PROPOSED]`.
* If an unhandled exception or timeout occurred, Orchestrator marks task status as `FAILED` `[PROPOSED]` with error context and emits a Task Failure Event `[PROPOSED]`.

### Stage 6: Multi-Channel Observer Updates
* **Dashboard:** The Next.js dashboard, executing frontend-controlled periodic polling (`PROPOSED: GET /api/v1/tasks/{id}`), fetches the updated state, renders step logs, diffs, and completion badges.
* **Voice Output:** The `packages/voice` module consumes the Task Completion / Failure event and triggers the Text-to-Speech (TTS) adapter to speak a short response.
* **Slack Notification:** The `packages/slack` module consumes the event, formats a Slack message block payload, and sends an async HTTP POST request to the configured Slack webhook URL.

---

## 4. Proposed Contract Schemas [PROPOSED — REQUIRES EDITH-000 APPROVAL]

### Proposed Request Schema (`PROPOSED: POST /api/v1/tasks`)
```json
{
  "prompt": "Fix import error in user_service.py and run pytest",
  "context": {
    "repository_path": ".",
    "source_channel": "web_ui"
  },
  "_contract_status": "PROPOSED — REQUIRES EDITH-000 APPROVAL"
}
```

### Proposed Response Schema (`202 Accepted`)
```json
{
  "task_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "status": "CREATED",
  "created_at": "2026-08-30T23:00:00Z",
  "_contract_status": "PROPOSED — REQUIRES EDITH-000 APPROVAL"
}
```
