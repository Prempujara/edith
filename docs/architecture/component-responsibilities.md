# EDITH-001 — Component Responsibilities & Boundaries

**Author:** Mannan Shah (System Designer & Solutions Architect)  
**Project:** EDITH (Enhanced Distributed Intelligent Task Handler)  
**Date:** August 30, 2026  
**Status:** Proposed Blueprint — Subject to EDITH-000 Approval  

---

## 1. Overview

This document specifies the technical responsibilities, input/output contracts, dependencies, and explicit boundaries ("What it must NOT do") for each component in the EDITH system architecture.

---

## 2. Component Specification

### 2.1 EDITH REST API Gateway (`apps/backend/api`)
* **Purpose:** Serves as the HTTP entrypoint and validation gateway for external callers (Dashboard, scripts, external triggers).
* **Responsibilities:**
  * Validate incoming task payload requests against request schemas.
  * Assign unique task identifiers.
  * Save initial task state to the task state store.
  * Dispatch task to Orchestrator workflow engine.
  * Expose REST endpoints for task creation, retrieval, listing, and health checks. *(Exact endpoint paths and schemas: PROPOSED — REQUIRES EDITH-000 APPROVAL)*.
  * Handle HTTP status codes, CORS headers, and request logging.
* **Inputs:** JSON HTTP Requests (`PROPOSED: POST /api/v1/tasks`, `PROPOSED: GET /api/v1/tasks/{id}`).
* **Outputs:** JSON HTTP Responses (`202 Accepted`, `200 OK`, `400 Bad Request`, `404 Not Found`).
* **Dependencies:** FastAPI, Pydantic, Task State Store, `Orchestrator`.
* **Must NOT Do:**
  * Must NOT execute LLM prompts directly.
  * Must NOT run shell commands or filesystem reads/writes directly.
  * Must NOT implement Slack webhook dispatch directly.
  * Must NOT format or synthesize voice audio.

---

### 2.2 Orchestrator Engine (`apps/backend/orchestrator`)
* **Purpose:** Manages the high-level task execution lifecycle, workflow routing, agent selection, and event publishing.
* **Responsibilities:**
  * Track and transition task execution states. *(Lifecycle states: PROPOSED — REQUIRES EDITH-000 APPROVAL)*.
  * Determine which agent (e.g., Coding Agent) handles the task prompt.
  * Delegate execution steps to the selected agent.
  * Handle execution timeouts, retries, and top-level error recovery.
  * Publish lifecycle events to the internal event system.
  * Update final task status and execution result in the task state store.
* **Inputs:** Task domain object.
* **Outputs:** State updates, Task Completion / Failure Events.
* **Dependencies:** Task State Store, `CodingAgent`, Internal Event System.
* **Must NOT Do:**
  * Must NOT contain UI rendering or HTML/JSX logic.
  * Must NOT handle Slack API formatting or HTTP webhook calls directly.
  * Must NOT handle voice audio processing or provider SDKs.
  * Must NOT execute low-level shell commands or file writes directly (must delegate to Tool Layer).
  * Must NOT depend directly on vendor-specific AI provider SDKs.

---

### 2.3 Coding Agent (`packages/agents/coding`)
* **Purpose:** Formulates reasoning strategies, constructs prompts for software engineering tasks, and requests tool executions.
* **Responsibilities:**
  * Receive user task instruction from Orchestrator.
  * Request workspace context via tool read calls.
  * Formulate execution steps and tool action requests (e.g., read file, write file, run test).
  * Return final resolution summary to Orchestrator.
* **Inputs:** Task prompt, repository context snippets, tool execution outputs.
* **Outputs:** Tool execution requests, final code change plan / summary.
* **Dependencies:** Shared Agent interfaces (`packages/agents/base`), Model Integration boundary, Tool Execution boundary.
* **Must NOT Do:**
  * Must NOT modify task lifecycle states directly.
  * Must NOT write directly to the host filesystem without going through the controlled Tool Execution boundary.
  * Must NOT interact directly with frontend, voice, or Slack components.

---

### 2.4 Tool / Repository Execution Layer (`apps/backend/tools`)
* **Purpose:** Provides a controlled boundary for reading, writing, inspecting, and running commands in the project workspace.
* **Responsibilities:**
  * Read file contents safely within project workspace boundaries.
  * Write/modify files safely with validation and safety checks.
  * Execute shell commands (e.g., `pytest`, `npm test`, `git status`) with strict execution timeout limits.
  * Validate path safety (prevent path traversal outside workspace).
* **Inputs:** Tool call requests (`tool_name`, `arguments`, `timeout_seconds`).
* **Outputs:** Standard output (stdout), standard error (stderr), exit code, file contents.
* **Dependencies:** Python standard library (`os`, `subprocess`, `pathlib`).
* **Must NOT Do:**
  * Must NOT execute commands outside the configured workspace root.
  * Must NOT contain LLM or agent prompt logic.
  * Must NOT make decisions on whether a task has succeeded or failed at the business level.

---

### 2.5 Frontend / Dashboard (`apps/frontend`)
* **Purpose:** Web application interface for user task submission, monitoring, and result visualization.
* **Responsibilities:**
  * Render task prompt submission form (Text + Voice button option).
  * Render active task status, step progress, and execution logs via configurable periodic HTTP polling.
  * Display completed task diffs, summaries, and error logs.
* **Inputs:** User text input, microphone audio (via browser speech STT option), backend API responses.
* **Outputs:** User task creation requests, visual DOM rendering, voice synthesis trigger.
* **Dependencies:** Next.js, React, CSS, Browser Web Speech API (as zero-cost MVP option).
* **Must NOT Do:**
  * Must NOT run Python agent logic in the browser.
  * Must NOT execute shell commands or git commands directly.
  * Must NOT store secret keys in client-side code.

---

### 2.6 Voice Integration Boundary (`packages/voice`)
* **Purpose:** Provides provider-independent Speech-to-Text (STT) command capture and Text-to-Speech (TTS) audio feedback.
* **Responsibilities:**
  * Expose provider-agnostic STT and TTS adapter interfaces.
  * Convert audio/speech input to clean text string payloads for task submission.
  * Convert task result summary text into spoken audio output.
  * (Browser-native Web Speech API may be evaluated as a zero-cost MVP implementation option).
* **Inputs:** Audio stream / spoken input, response text strings.
* **Outputs:** Formatted text strings, spoken audio playback.
* **Dependencies:** `packages/voice` interface adapter, optional client/browser speech capabilities.
* **Must NOT Do:**
  * Must NOT process task execution logic or manage agent state.
  * Must NOT depend on mandatory paid cloud speech services.

---

### 2.7 Slack Integration Boundary (`packages/slack`)
* **Purpose:** Decoupled event consumer that broadcasts task completion and error notifications to a Slack channel.
* **Responsibilities:**
  * Subscribe asynchronously to Task Completion and Failure events.
  * Format event data into structured Slack message payload.
  * Dispatch HTTP POST requests to Slack Incoming Webhook URL.
  * Handle network failures gracefully without affecting main task execution.
* **Inputs:** Internal domain events (Task Completion / Failure Events).
* **Outputs:** HTTP POST requests to Slack Incoming Webhook URL.
* **Dependencies:** HTTP client library (`httpx` / `requests`), Slack Incoming Webhook URL.
* **Must NOT Do:**
  * Must NOT modify task execution flow or block Orchestrator execution.
  * Must NOT depend on paid Slack app subscriptions.

---

### 2.8 Internal Event System (`apps/backend/events`)
* **Purpose:** Provides decoupled publish-subscribe messaging within the backend process.
* **Responsibilities:**
  * Maintain in-process event listener registry.
  * Publish events asynchronously to registered handlers without blocking event producers.
* **Inputs:** Internal Event objects.
* **Outputs:** In-process callback invocations to registered event subscribers.
* **Dependencies:** Python `asyncio` in-process event dispatcher.
* **Must NOT Do:**
  * Must NOT require heavy external message queues (e.g., RabbitMQ, Kafka, Redis) for MVP.

---

## 3. Comprehensive Component Responsibility Matrix

| Component | Primary Purpose | Inputs | Outputs | Core Responsibilities | Must NOT Do |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **EDITH API** | HTTP Gateway & Validation | REST HTTP Requests | REST HTTP Responses | Endpoint routing, validation, task dispatching | Execute LLM prompts, run shell commands |
| **Orchestrator** | Task Workflow Manager | Task Object | State updates, Events | Lifecycle management, agent selection, retry logic | Render UI, format Slack/Voice, run low-level tools |
| **Coding Agent** | Reasoning & Code Strategy | Task Prompt, Repo context | Tool Requests, Code Plan | Formulate LLM prompts, interpret code diffs | Change task state directly, write filesystem directly |
| **Tool Execution Layer** | Controlled Execution | Tool Arguments, Command | stdout, stderr, exit code | Execute filesystem reads/writes, run shell commands | Run LLM logic, decide business task success/failure |
| **Frontend / Dashboard** | User UI & Visualizer | User Input, API Responses | HTTP Requests, DOM render | Render form, display task logs, poll task status | Run Python agent logic, store secret keys |
| **Voice Adapter** | Speech Ingestion & Synthesis | Audio Stream / Result Text | Command Text / Audio Playback | Speech-to-text (STT) and text-to-speech (TTS) adapter boundary | Process agent logic, depend on paid cloud STT/TTS |
| **Slack Adapter** | Channel Notification | Task Lifecycle Events | Slack Webhook HTTP POST | Format and post task completion/failure notices | Block Orchestrator, modify task state |
| **Event System** | Decoupled In-Process Messaging| Domain Events | Async Callback Invocations | Broadcast events to internal subscribers | Require external heavy message queue |
