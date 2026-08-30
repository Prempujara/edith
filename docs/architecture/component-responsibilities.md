# EDITH-001 — Component Responsibilities & Boundaries

**Author:** Mannan Shah (System Designer & Solutions Architect)  
**Project:** EDITH (Enhanced Distributed Intelligent Task Handler)  
**Date:** August 30, 2026  
**Status:** Complete / Proposed Blueprint  

---

## 1. Overview

This document specifies the exact technical responsibilities, input/output contracts, dependencies, and explicit boundaries ("What it must NOT do") for each component in the EDITH system architecture.

---

## 2. Component Specification

### 2.1 EDITH REST API Gateway (`apps/backend/api`)
* **Purpose:** Serves as the HTTP entrypoint and validation gateway for all external callers (Dashboard, scripts, external triggers).
* **Responsibilities:**
  * Validate incoming task payload requests against Pydantic schemas.
  * Assign unique task identifiers (`task_id` UUID).
  * Persist initial task state to `TaskStore`.
  * Dispatch task to Orchestrator queue.
  * Expose REST endpoints for task creation, retrieval, listing, and health checks.
  * Handle HTTP error codes, CORS headers, and request logging.
* **Inputs:** JSON HTTP Requests (`POST /api/v1/tasks`, `GET /api/v1/tasks/{id}`).
* **Outputs:** JSON HTTP Responses (`202 Accepted`, `200 OK`, `400 Bad Request`, `404 Not Found`).
* **Dependencies:** FastAPI, Pydantic, In-Memory `TaskStore`, `Orchestrator`.
* **Must NOT Do:**
  * Must NOT execute LLM prompts directly.
  * Must NOT run shell commands or filesystem reads/writes.
  * Must NOT implement Slack webhook dispatch directly.
  * Must NOT format voice text.

---

### 2.2 Orchestrator Engine (`apps/backend/orchestrator`)
* **Purpose:** Manages the high-level task execution lifecycle, workflow state machine, agent selection, and event publishing.
* **Responsibilities:**
  * Track and transition task states (`CREATED`, `QUEUED`, `IN_PROGRESS`, `COMPLETED`, `FAILED`).
  * Determine which agent (e.g., Coding Agent) handles the task prompt.
  * Delegate sub-steps to the selected agent.
  * Handle execution timeouts, retries, and top-level error recovery.
  * Publish lifecycle events to the internal `EventBus`.
  * Update final task status and execution result in `TaskStore`.
* **Inputs:** `Task` entity domain object.
* **Outputs:** State updates, `TaskCompletedEvent`, `TaskFailedEvent`.
* **Dependencies:** `TaskStore`, `CodingAgent`, `EventBus`.
* **Must NOT Do:**
  * Must NOT contain UI rendering or HTML/JSX logic.
  * Must NOT handle Slack API formatting or authentication.
  * Must NOT handle voice audio processing.
  * Must NOT execute low-level shell commands directly (must delegate to Tool Layer).

---

### 2.3 Coding Agent (`packages/agents/coding`)
* **Purpose:** Formulates reasoning strategies, constructs LLM prompts for software engineering tasks, and requests tool executions.
* **Responsibilities:**
  * Receive user task instruction from Orchestrator.
  * Analyze repository structure via tool read requests.
  * Construct structured prompt context for LLM execution.
  * Parse LLM outputs into structured tool actions (e.g., `READ_FILE`, `WRITE_FILE`, `RUN_TEST`).
  * Return final resolution summary to Orchestrator.
* **Inputs:** Task prompt, repository context snippets, tool execution outputs.
* **Outputs:** Tool execution requests, final code change plan / summary.
* **Dependencies:** Shared Agent interfaces (`packages/agents/base`), LLM Provider client, Tool Execution boundary.
* **Must NOT Do:**
  * Must NOT modify task lifecycle states directly.
  * Must NOT write directly to the host filesystem without going through the Tool Layer sandbox.
  * Must NOT interact directly with frontend, voice, or Slack components.

---

### 2.4 Tool / Repository Execution Layer (`apps/backend/tools`)
* **Purpose:** Provides controlled, sandboxed access to the filesystem, git repository, and local command execution environment.
* **Responsibilities:**
  * Read file contents safely within project workspace boundaries.
  * Write/modify files safely with automatic backup or rollback capability.
  * Execute shell commands (e.g., `pytest`, `npm test`, `git status`) with strict timeout limits.
  * Validate path safety (prevent path traversal outside workspace).
* **Inputs:** Tool call commands (`tool_name`, `arguments`, `timeout_seconds`).
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
  * Render task prompt submission form (Text + Voice button).
  * Render active task status, step progress, and execution logs via HTTP polling.
  * Display completed task diffs, summaries, and error logs.
* **Inputs:** User text input, microphone audio (via Web Speech API), backend API responses (`GET /api/v1/tasks`).
* **Outputs:** User commands (`POST /api/v1/tasks`), visual DOM rendering, voice synthesis trigger.
* **Dependencies:** Next.js, React, TailwindCSS/Vanilla CSS, Browser Web Speech API.
* **Must NOT Do:**
  * Must NOT run Python agent logic in the browser.
  * Must NOT execute shell commands or git commands directly.
  * Must NOT store secrets (e.g., API keys) in client-side code.

---

### 2.6 Voice Integration Boundary (`packages/voice`)
* **Purpose:** Provides speech-to-text (STT) command capture and text-to-speech (TTS) audio feedback.
* **Responsibilities:**
  * Capture spoken input via Web Speech STT API (client) or local STT library fallback.
  * Convert audio to clean text string payload for API submission.
  * Convert task result summary text into spoken audio output via Web Speech TTS or `gTTS`.
* **Inputs:** Microphone audio stream / spoken audio, response text strings.
* **Outputs:** Formatted text strings, spoken audio playback.
* **Dependencies:** Web Speech API, `packages/voice` interface adapter.
* **Must NOT Do:**
  * Must NOT process task execution logic or manage agent state.
  * Must NOT depend on mandatory paid cloud speech services (e.g., ElevenLabs, Amazon Polly).

---

### 2.7 Slack Integration Boundary (`packages/slack`)
* **Purpose:** Decoupled event consumer that broadcasts task completion and error notifications to a Slack channel.
* **Responsibilities:**
  * Subscribe to `TaskCompletedEvent` and `TaskFailedEvent` from EventBus.
  * Format event data into structured Slack Block Kit / JSON payload.
  * Dispatch HTTP POST requests to Slack Incoming Webhook URL.
  * Handle network failures gracefully without affecting main task execution.
* **Inputs:** Internal domain events (`TaskCompletedEvent`, `TaskFailedEvent`).
* **Outputs:** HTTP POST requests to Slack Webhook URL.
* **Dependencies:** `requests` / `httpx`, Slack Incoming Webhook URL.
* **Must NOT Do:**
  * Must NOT modify task execution flow or block Orchestrator execution.
  * Must NOT depend on paid Slack app subscriptions.

---

### 2.8 Internal Event System (`apps/backend/events`)
* **Purpose:** Provides decoupled publish-subscribe messaging within the backend process.
* **Responsibilities:**
  * Maintain event listener registry.
  * Publish events asynchronously to registered handlers without blocking event producers.
* **Inputs:** Event objects (`Event`).
* **Outputs:** In-process callback invocations to registered event subscribers.
* **Dependencies:** Python `asyncio` or `PyPubSub`.
* **Must NOT Do:**
  * Must NOT require heavy external message queues (e.g., RabbitMQ, Kafka, Redis) for MVP.

---

## 3. Comprehensive Component Responsibility Matrix

| Component | Primary Purpose | Inputs | Outputs | Core Responsibilities | Must NOT Do |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **EDITH API** | HTTP Gateway & Validation | REST HTTP Requests | REST HTTP Responses | Endpoint routing, validation, task dispatching | Execute LLM prompts, run shell commands |
| **Orchestrator** | Task Workflow Manager | Task Entity | State updates, Events | Lifecycle management, agent selection, retry logic | Render UI, format Slack/Voice, run low-level tools |
| **Coding Agent** | Reasoning & Code Strategy | Task Prompt, Repo context | Tool Requests, Code Plan | Formulate LLM prompts, interpret code diffs | Change task state directly, write filesystem directly |
| **Tool Execution Layer** | Sandboxed Execution | Tool Arguments, Command | stdout, stderr, exit code | Execute filesystem reads/writes, run shell commands | Run LLM logic, decide business task success/failure |
| **Frontend / Dashboard** | User UI & Visualizer | User Input, API Responses | HTTP Requests, DOM render | Render form, display task logs, poll task status | Run Python agent logic, store secret keys |
| **Voice Adapter** | Speech Ingestion & Synthesis | Audio Stream / Result Text | Command Text / Audio Playback | Convert speech to text (STT) and text to speech (TTS) | Process agent logic, depend on paid cloud STT/TTS |
| **Slack Adapter** | Channel Notification | Task Lifecycle Events | Slack Webhook HTTP POST | Format and post task completion/failure notices | Block Orchestrator, modify task state |
| **Event System** | Decoupled In-Process Messaging| Domain Events | Async Callback Invocations | Broadcast events to internal subscribers | Require external heavy message queue |
