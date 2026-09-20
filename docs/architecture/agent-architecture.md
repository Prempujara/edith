# EDITH-001 — Agent Architecture & Delegation Specification

**Author:** Mannan Shah (System Designer & Solutions Architect)  
**Project:** EDITH (Enhanced Distributed Intelligent Task Handler)  
**Date:** September 20, 2026  
**Status:** APPROVED ARCHITECTURE BASELINE  

---

## 1. Multi-Agent Ecosystem Model

The EDITH platform is designed around **Three Specialized Agents** sharing a common underlying infrastructure (**Shared Runtime**, **Shared Context**, **Tool Registry**, and **Event System**).

Rather than relying on a single monolithic assistant or an external central supervisor, EDITH delegates responsibilities across specialized domain agents.

```
                    ┌──────────────────────────┐
                    │       USER PROMPT        │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │  JARVIS (PRIMARY AGENT)  │
                    │  Conversational Lead     │
                    │  Software & Research     │
                    └──────┬────────────┬──────┘
                           │            │
             Delegates     │            │ Delegates
             Computer Task │            │ File Task
                           ▼            ▼
         ┌───────────────────┐        ┌───────────────────┐
         │       EDITH       │        │      FRIDAY       │
         │ Computer & Browser│        │ Files & Documents │
         └─────────┬─────────┘        └─────────┬─────────┘
                   │                            │
                   └─────────────┬──────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │      SHARED RUNTIME      │
                    │ (Transport & Execution)  │
                    └──────────────────────────┘
```

---

## 2. Agent Definitions & Contracts

### 2.1 JARVIS — Primary Conversational & Engineering Specialist

* **Purpose:** Acts as the primary front-facing agent for user communication, software engineering, code synthesis, research, and high-level task delegation.
* **Domain Responsibilities:**
  - Software development, code writing, refactoring, and code analysis.
  - Debugging, automated test execution, and Git repository operations.
  - Technical research, web browsing, and multi-step plan synthesis.
  - Analyzing incoming user requests and determining if delegation to EDITH or FRIDAY is required.
  - Aggregating delegation outputs and presenting unified results to the user.
* **Input Interfaces:** User text/voice prompts, task execution responses from Shared Runtime, subtask results from EDITH/FRIDAY.
* **Output Interfaces:** User response messages, code file updates, tool execution requests, subtask delegation requests.
* **Permitted Tools:** `file_read`, `file_write`, `shell_execute`, `git_commit`, `git_status`, `web_search`.
* **Delegation Capabilities:** Can delegate computer interaction tasks to **EDITH** and document/filing tasks to **FRIDAY**.
* **Forbidden Actions ("Must NOT do"):**
  - Must NOT attempt direct OS desktop GUI click/keystroke automation (must delegate to EDITH).
  - Must NOT take over workspace file indexing/bulk document organization (must delegate to FRIDAY).

### 2.2 EDITH — Computer & Browser Specialist

* **Purpose:** Specialized agent dedicated to host desktop interaction, browser automation, and computer-control tasks.
* **Domain Responsibilities:**
  - Navigating web browsers, filling forms, and interacting with web apps.
  - Capturing desktop screenshots and inspecting active UI elements.
  - Performing mouse clicks, keyboard input, and window management tasks.
* **Input Interfaces:** Delegated computer-control task requests from JARVIS or direct system events.
* **Output Interfaces:** Computer execution logs, screenshots, UI automation results, task completion status.
* **Permitted Tools:** `browser_open`, `browser_click`, `browser_type`, `desktop_screenshot`, `desktop_click`, `desktop_key_press`.
* **Delegation Capabilities:** Can request code analysis from **JARVIS** or document archiving from **FRIDAY**.
* **Forbidden Actions ("Must NOT do"):**
  - Must NOT act as the primary conversational assistant for general software development or user Q&A.
  - Must NOT directly write Python/TypeScript backend code files (must delegate to JARVIS).

### 2.3 FRIDAY — Files, Documents & Organization Specialist

* **Purpose:** Specialized agent dedicated to workspace document management, file organization, cataloging, and structural operations.
* **Domain Responsibilities:**
  - Workspace directory organization and file structure maintenance.
  - Parsing document formats (Markdown, PDF, JSON, CSV, Text).
  - Categorizing, tagging, and archiving project artifacts and logs.
  - Generating documentation indexes and summary reports.
* **Input Interfaces:** File-management task requests from JARVIS or EDITH.
* **Output Interfaces:** Structured file summaries, organization reports, file move/copy operations.
* **Permitted Tools:** `file_read`, `file_write`, `file_move`, `file_delete`, `directory_list`, `document_parse`.
* **Delegation Capabilities:** Can report file status to **JARVIS** or request browser verification from **EDITH**.
* **Forbidden Actions ("Must NOT do"):**
  - Must NOT attempt OS desktop GUI mouse/keyboard emulation (must delegate to EDITH).
  - Must NOT formulate complex software architecture or primary code logic (must delegate to JARVIS).

---

## 3. Agent Matrix Comparison

| Attribute | JARVIS | EDITH | FRIDAY |
| :--- | :--- | :--- | :--- |
| **Primary Domain** | Conversation, Coding, Research | Computer / Browser Control | Files, Documents, Organization |
| **User Fronting** | Primary User Interface | Specialist (Delegated) | Specialist (Delegated) |
| **Tool Scope** | Code, Git, Shell, Web Search | Browser, Desktop GUI, Screen | Filesystem, Document Parsers |
| **Delegation Role** | Primary Delegator | Subtask Specialist | Subtask Specialist |
| **Default Persona** | Technical, Precise, Efficient | Direct, Operational, Action-Oriented | Organized, Systematic, Neat |

---

## 4. Agent Delegation Architecture

### 4.1 Delegation Decision Rule

```
                               ┌────────────────────────────────┐
                               │  JARVIS Receives User Prompt   │
                               └───────────────┬────────────────┘
                                               │
                                               ▼
                               ┌────────────────────────────────┐
                               │     Does task require OS GUI,  │
                               │   Browser, or Bulk Filing?     │
                               └───────┬────────────────┬───────┘
                                       │                │
                             NO        │                │ YES
                   ┌───────────────────┘                └───────────────────┐
                   ▼                                                        ▼
┌──────────────────────────────────────┐                ┌──────────────────────────────────────┐
│  JARVIS Executes Directly via Tools  │                │    JARVIS Formulates Subtask Payload │
└──────────────────────────────────────┘                └───────────────────┬──────────────────┘
                                                                            │
                                                                            ▼
                                                        ┌──────────────────────────────────────┐
                                                        │  Shared Runtime Routes Subtask to    │
                                                        │         EDITH or FRIDAY              │
                                                        └──────────────────────────────────────┘
```

1. **Source Agent Decides:** Delegation decisions originate inside the agent's reasoning loop (via tool call or structured LLM response).
2. **Runtime Transport:** When an agent decides to delegate, it emits a `DelegationRequest` to the Shared Runtime:
   - `source_agent`: E.g., `"JARVIS"`
   - `target_agent`: E.g., `"EDITH"` or `"FRIDAY"`
   - `parent_task_id`: Unique ID of the originating task
   - `subtask_payload`: Detailed instructions and context for the target agent
3. **Execution Coordination:** The Shared Runtime creates a child task (`child_task_id`), registers parent-child linkage, updates state to `DELEGATED`, and dispatches the task to the target agent.
4. **Result Propagation:** Upon subtask completion, the target agent returns a `SubtaskResult`. The Shared Runtime delivers the result back to the parent task context and notifies the source agent.

### 4.2 Guardrails & Failure Management

* **Circular Delegation Guardrail:** The Shared Runtime tracks delegation depth. If a task exceeds `MAX_DELEGATION_DEPTH = 3` or detects a cyclic chain (`JARVIS -> EDITH -> JARVIS -> EDITH`), the runtime aborts the subtask with a `CircularDelegationError`.
* **Subtask Timeout:** Subtasks carry explicit timeout bounds (e.g., 60 seconds). If a subtask times out, the Shared Runtime marks the child task `TIMED_OUT` and returns a partial failure to the parent agent.
* **Parent Task Cancellation:** If a user cancels a parent task, the Shared Runtime cascades cancellation signals to all active child subtasks (`EDITH`/`FRIDAY`).
