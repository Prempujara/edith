# EDITH System Architecture

**Project:** EDITH — Enhanced Distributed Intelligent Task Handler  
**Project Type:** Multi-Agent AI Assistant Ecosystem  
**Status:** Architecture Baseline  
**Version:** 1.0  
**Primary Technical Lead:** Prem  
**Team Size:** 4

---

## 1. System Vision

EDITH is a multi-agent AI assistant ecosystem inspired by the concept of interconnected AI assistants such as EDITH, JARVIS, and FRIDAY.

The system consists of three separate AI agents that share common infrastructure while maintaining distinct responsibilities, personalities, voices, and tool permissions.

The three agents are:

- **JARVIS** — Primary conversational and technical agent
- **EDITH** — Intelligence and computer-control agent
- **FRIDAY** — File-management and operations agent

The agents are not isolated chatbots. They can communicate with one another, delegate tasks, execute tasks in parallel, share memory, and return results to the user.

The central design principle is:

> **The agents themselves make delegation decisions rather than relying on a single central AI orchestrator.**

---

## 2. High-Level Architecture

```text
                         USER
                          │
                 Voice / Text / UI
                          │
                          ▼
                    JARVIS PRIMARY
                          │
                 ┌────────┴────────┐
                 │                 │
              EDITH             FRIDAY
                 │                 │
                 └────────┬────────┘
                          │
                  AGENT RUNTIME
                          │
       ┌──────────────────┼──────────────────┐
       │                  │                  │
     Memory             Tools              Events
       │                  │                  │
       │          ┌───────┼────────┐         │
       │          │       │        │         │
       │       Computer  Files    Code       │
       │          │       │        │         │
       └──────────┴───────┴────────┴─────────┘
                          │
                     CLOUD AI
```

The Agent Runtime provides shared infrastructure. It does not replace the agents' intelligence or become a single centralized decision-maker.

---

# 3. Agent Definitions

## 3.1 JARVIS

### Primary Role

JARVIS is the **primary conversational and technical agent**.

### Responsibilities

- Software development
- Coding
- Code analysis
- Debugging
- Running code
- Git operations
- GitHub operations
- Web browsing and research
- Repository analysis
- Technical planning
- Delegating tasks to EDITH and FRIDAY
- Coordinating multi-agent tasks
- Communicating final results to the user

### Personality

Professional, technical, calm, precise, and efficient.

### Position in System

JARVIS is the primary agent users interact with by default.

---

## 3.2 EDITH

### Primary Role

EDITH is the **intelligence and computer-control agent**.

### Responsibilities

- Computer control
- Screen/context awareness
- Application interaction
- Mouse and keyboard interaction
- Browser interaction
- Computer-level operations
- Intelligence/research-oriented tasks where appropriate
- Delegating technical work to JARVIS
- Delegating file operations to FRIDAY

### Personality

Analytical, observant, precise, and concise.

### Position in System

EDITH specializes in interacting with the user's computer and can participate in multi-agent workflows.

---

## 3.3 FRIDAY

### Primary Role

FRIDAY is the **file-management and operations agent**.

### Responsibilities

- File management
- Folder management
- Creating files and folders
- Reading files
- Renaming files
- Moving files
- Organizing project files
- Working with documents and project artifacts
- Operational tasks
- Delegating technical tasks to JARVIS
- Delegating computer-control tasks to EDITH

### Personality

Efficient, helpful, organized, and conversational.

### Position in System

FRIDAY specializes in local file and document operations.

---

# 4. Agent Relationship

The agents are separate agents sharing common infrastructure.

They are peers in terms of architectural independence, but **JARVIS is the primary user-facing agent**.

Agents can:

- Communicate with each other
- Delegate tasks
- Request results
- Share context
- Work simultaneously
- Disagree and discuss possible approaches
- Use the capabilities of another specialized agent through delegation

Example:

```text
User
 │
 ▼
JARVIS
 │
 ├── "EDITH, open the project and inspect the application."
 │
 ▼
EDITH
 │
 └── Result
       │
       ▼
     JARVIS
       │
       └── Continues technical work
```

Another example:

```text
JARVIS
 │
 ├── EDITH  → Computer operation
 │
 ├── JARVIS → Coding
 │
 └── FRIDAY → File organization
```

These tasks may execute in parallel when there are no dependencies between them.

---

# 5. Agent-to-Agent Communication

## 5.1 Communication Model

Agent communication is **asynchronous**.

A requesting agent does not have to block all of its other work while another agent performs a task.

Conceptually:

```text
JARVIS
   │
   ├── Request → EDITH
   │
   ├── Continue working
   │
   └── Request → FRIDAY

EDITH ───────────────→ Result
FRIDAY ──────────────→ Result
```

---

## 5.2 Agent Delegation

Each agent can delegate a task when another agent has a better capability for the requested operation.

Examples:

```text
JARVIS → EDITH
"Open the project in the required application."
```

```text
JARVIS → FRIDAY
"Organize the generated documentation."
```

```text
EDITH → JARVIS
"Analyze the code in this repository."
```

```text
FRIDAY → JARVIS
"Review this generated configuration file for technical correctness."
```

---

## 5.3 Parallel Execution

The system must support multiple independent tasks executing at the same time.

Example:

```text
                 JARVIS
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
       EDITH      JARVIS    FRIDAY
      Computer     Code       Files
          │         │         │
          └─────────┼─────────┘
                    ▼
               Combined Result
```

---

## 5.4 Visible Communication

Agent-to-agent communication should be visible in the user interface as system activity.

For example:

```text
JARVIS
└─ Delegating computer operation to EDITH...

EDITH
└─ Opening the requested application...

EDITH
└─ Operation completed.

JARVIS
└─ Continuing analysis...
```

This is important for demonstrating the multi-agent nature of the project.

---

# 6. Tool Permissions

Tool access is specialized by agent.

## 6.1 EDITH Tools

EDITH may access:

- Screen observation
- Mouse control
- Keyboard control
- Application interaction
- Browser interaction
- Browser navigation
- Computer-level tools

## 6.2 JARVIS Tools

JARVIS may access:

- Filesystem read access required for coding
- Code editing
- Terminal
- Code execution
- Git
- GitHub
- Web browsing
- Repository inspection
- Development tools

## 6.3 FRIDAY Tools

FRIDAY may access:

- File creation
- File reading
- File renaming
- File moving
- Folder creation
- File organization
- Document operations

---

# 7. Permission Levels

Tool permissions should be separated into levels:

```text
READ
WRITE
EXECUTE
DESTRUCTIVE
```

Agents should only receive the permissions required for their responsibilities.

---

# 8. Confirmation Policy

Potentially destructive operations require user confirmation.

Examples include:

- Deleting files
- Overwriting important files
- Git reset operations
- Git operations that discard work
- Potentially destructive terminal commands
- Other irreversible actions

Example:

```text
FRIDAY:
"This operation will move 37 files into an archive.
Proceed?"

        [YES] [NO]
```

The agent must not silently perform destructive operations.

Safe read-only operations generally do not require confirmation.

---

# 9. Shared Memory

All three agents share common memory.

The shared memory model includes:

## 9.1 Conversation Memory

Stores relevant conversational context.

## 9.2 Task Memory

Stores task-related information such as:

- Task ID
- Request
- Assigned agent
- Status
- Result
- Relevant events

## 9.3 Agent Memory

Stores useful information generated or discovered by agents.

Example:

```text
EDITH discovered information
          ↓
     Shared Memory
          ↓
JARVIS can use that information
```

## 9.4 Project Memory

Stores relevant project-level context, such as:

- Project structure
- Technologies used
- Repository information
- Important configuration
- Previously completed work
- Relevant project decisions

---

# 10. Memory Principles

Memory should be shared across the three agents.

The system should preserve enough context for an agent to continue work performed by another agent.

Example:

```text
EDITH
Researches a technical topic
        │
        ▼
Shared Memory
        │
        ▼
JARVIS
Uses EDITH's findings
```

The memory system should be modular so its implementation can evolve without changing the agent interfaces.

---

# 11. Voice System

Each agent has its own voice.

## 11.1 Activation

Users can activate agents in two ways:

1. Voice activation
2. User-interface selection

Example:

```text
"Hey JARVIS..."
"Hey EDITH..."
"Hey FRIDAY..."
```

The UI can also allow the user to select an agent directly.

---

## 11.2 Voice Identity

Each agent should have a distinct recognizable voice profile.

Conceptually:

```text
JARVIS  → calm / professional
EDITH   → precise / analytical
FRIDAY  → friendly / efficient
```

The implementation must not depend on imitating a real actor's voice.

---

## 11.3 Agent-to-Agent Voice

Agent-to-agent communication is **silent by default**.

The user interface can display the communication as text/system activity without making agents audibly speak to each other.

This prevents multi-agent workflows from becoming noisy.

---

# 12. Agent Runtime

The Agent Runtime is the shared technical infrastructure used by all three agents.

It is not a central AI decision-maker.

Its responsibilities include:

```text
Agent Runtime
├── Agent Registry
├── Agent Messaging
├── Shared Context
├── Memory
├── Event System
├── Task Tracking
├── Tool Registry
├── Permission Management
└── Execution Coordination
```

---

# 13. Agent Registry

The Agent Registry maintains the available agents and their capabilities.

Conceptually:

```text
Agent Registry

JARVIS
Capabilities:
- coding
- debugging
- git
- github
- web

EDITH
Capabilities:
- computer_control
- browser
- screen

FRIDAY
Capabilities:
- file_management
- document_operations
```

Agents use capabilities to determine which agent is appropriate for delegation.

---

# 14. Task Model

A task represents an operation requested by the user or delegated by another agent.

A task should conceptually contain:

- Task ID
- Parent Task ID where applicable
- Requester
- Assigned agent
- Input
- Status
- Priority
- Created timestamp
- Started timestamp
- Completed timestamp
- Result
- Error information
- Related events

Delegated tasks should be linked to their parent task.

Example:

```text
Task #100
JARVIS
 │
 ├── Task #101 → EDITH
 └── Task #102 → FRIDAY
```

---

# 15. Task Lifecycle

The minimum lifecycle is:

```text
CREATED
   ↓
QUEUED
   ↓
RUNNING
   ↓
COMPLETED
```

Failure path:

```text
RUNNING
   ↓
FAILED
```

Cancelled tasks may also be supported if required.

Invalid state transitions must be prevented.

---

# 16. Event System

The runtime maintains events representing meaningful system activity.

Example events:

```text
task.created
task.queued
task.started
agent.selected
agent.delegated
agent.started
tool.started
tool.completed
agent.completed
task.completed
task.failed
```

Events should contain enough information for:

- Dashboard activity
- Debugging
- Task history
- Agent communication visualization
- Future audit functionality

---

# 17. Cloud + Local Hybrid Architecture

The system will use a **hybrid architecture**.

The AI reasoning/model layer may run through cloud AI services, while the local Agent Runtime executes controlled operations on the user's computer.

Important principle:

> **The cloud AI model does not automatically receive unrestricted access to the user's computer.**

Instead:

```text
Cloud AI
   │
   │ Reasoning / Planning
   ▼
Local Agent Runtime
   │
   ├── Filesystem
   ├── Browser
   ├── Computer Control
   ├── Terminal
   └── Development Tools
```

The local runtime executes approved tools and returns the necessary results to the model.

This allows the agents to use local files and computer capabilities while maintaining explicit permission boundaries.

---

# 18. Local File Access

Because the Agent Runtime runs locally, agents can interact with files on the local PC when permitted.

Example:

```text
User
 ↓
JARVIS
 ↓
"Inspect D:\Agent\edith"
 ↓
Permission Manager
 ↓
Local File Tool
 ↓
Relevant file contents
 ↓
Cloud AI reasoning
 ↓
JARVIS result
```

The entire filesystem should not be exposed unnecessarily.

Access should be limited to the required paths and operations wherever practical.

---

# 19. Agent Lifecycle

The three agents should support a hybrid lifecycle.

Conceptually:

```text
Agent Runtime
      │
      ├── EDITH   → available
      ├── JARVIS  → available
      └── FRIDAY  → available
```

The runtime remains available while individual agent processes/services may be started, stopped, or activated as needed.

This is particularly important for local development because the target development machine has limited resources.

---

# 20. User Interface

The UI has two complementary modes.

## 20.1 Individual Agent Interfaces

Each agent has its own dedicated interface.

```text
EDITH
JARVIS
FRIDAY
```

Users can select and interact with each agent independently.

## 20.2 Central HUD

The application also contains a central futuristic AI command-center/HUD.

Conceptually:

```text
┌─────────────────────────────────────────┐
│                 EDITH                   │
├─────────────────────────────────────────┤
│                                         │
│          AI COMMAND CENTER              │
│                                         │
│   EDITH     JARVIS      FRIDAY          │
│   ONLINE    ONLINE      ONLINE          │
│                                         │
│   Active Conversation                   │
│                                         │
│   JARVIS                                │
│   Delegating task to EDITH...           │
│                                         │
│              🎤 Listening               │
└─────────────────────────────────────────┘
```

The HUD should make agent activity and collaboration visually clear.

---

# 21. Demonstration Scenario

The primary demonstration should show genuine multi-agent collaboration.

Example user request:

> "JARVIS, research this topic, inspect my project, and prepare it for the demo."

Possible execution:

```text
                         JARVIS
                            │
             ┌──────────────┼──────────────┐
             │              │              │
             ▼              ▼              ▼
           EDITH          JARVIS         FRIDAY
        Computer/        Coding/         Files/
        Research         Technical      Organization
             │              │              │
             └──────────────┼──────────────┘
                            ▼
                      Shared Memory
                            │
                            ▼
                         JARVIS
                            │
                            ▼
                      Final Response
```

The UI displays the delegation and execution events.

The agents communicate internally without speaking over one another.

---

# 22. Architectural Principles

The implementation must follow these principles:

1. **Three independent agents**
2. **Shared infrastructure**
3. **JARVIS as primary user-facing agent**
4. **Agents can delegate to each other**
5. **Agents can work in parallel**
6. **Shared memory**
7. **Specialized tool permissions**
8. **User confirmation for destructive actions**
9. **Local runtime for computer/file/tool access**
10. **Cloud models for reasoning where appropriate**
11. **Modular architecture**
12. **Demo-first MVP development**
13. **Avoid unnecessary production infrastructure**
14. **Do not give agents unrestricted computer access**

---

# 23. MVP Scope

The MVP must prioritize a convincing working demonstration.

### P0 — Critical

- JARVIS
- EDITH
- FRIDAY
- Agent Runtime
- Agent-to-agent communication
- Delegation
- Shared task context
- Basic shared memory
- JARVIS coding workflow
- EDITH computer-control workflow
- FRIDAY file-management workflow
- Local tool execution
- Voice input
- Distinct agent voices
- Central HUD
- Individual agent interfaces

### P1 — Important

- Parallel execution
- Event visualization
- Git/GitHub integration
- Web browsing
- Better memory
- Permission confirmation UI
- Task history

### P2 — Optional

- Advanced planning
- More sophisticated agent disagreement/reasoning
- Advanced automation
- Additional integrations
- Production-grade distributed infrastructure

P2 features must not delay the working MVP.

---

# 24. Explicitly Out of Scope for MVP

Unless required later, avoid:

- Kubernetes
- Complex microservice infrastructure
- Large distributed queues
- Enterprise authentication
- Production-scale infrastructure
- Complex autonomous planning systems
- Unlimited computer access
- Unlimited filesystem access
- Excessive observability infrastructure
- Unnecessary cloud infrastructure

The goal is a reliable, impressive college demonstration rather than a production enterprise platform.

---

# 25. Team Ownership

## Prem — Project Manager + Technical Lead

Owns:

- Core technical implementation
- Agent Runtime
- JARVIS
- Core backend
- Agent communication implementation
- Coding capabilities
- Integration
- GitHub workflow
- Final technical integration
- Project management

## Member 2 — System Designer + Solutions Architect

Owns:

- System architecture
- Architecture diagrams
- Agent interaction design
- Technical design review
- Architecture documentation
- Integration architecture

## Member 3 — Project Analyst + QA Engineer

Owns:

- Requirements
- User stories
- Acceptance criteria
- Test planning
- QA
- Test execution
- Bug tracking
- Risk register
- Final testing report
- SPM analysis

## Member 4 — Frontend + Integration Developer

Owns:

- Central HUD
- Individual agent interfaces
- Frontend implementation
- Voice UI
- Frontend/backend integration
- Agent activity visualization
- Slack/integration work where required

---

# 26. Development Strategy

Development should proceed vertically around a demonstrable critical path.

```text
Agent Runtime
      ↓
JARVIS
      ↓
Agent Communication
      ↓
EDITH + FRIDAY
      ↓
Shared Memory
      ↓
Voice
      ↓
HUD
      ↓
Parallel Multi-Agent Demo
```

A smaller working system is preferable to a large incomplete system.

---

# 27. Definition of a Successful MVP

The MVP is successful when the team can demonstrate:

1. User activates an agent using voice or UI.
2. The selected agent understands the request.
3. The agent can perform its specialized task.
4. The agent can delegate to another agent.
5. The second agent receives the task.
6. The second agent executes using its authorized tools.
7. Results return to the requesting agent.
8. Shared context is maintained.
9. Multiple independent tasks can execute in parallel.
10. Agent communication is visible in the HUD.
11. Each agent responds using its distinct voice.
12. Destructive operations require confirmation.
13. Local computer/files can be accessed through controlled tools.
14. The user receives a clear final result.

---

# 28. Architecture Status

This document is the **baseline architecture specification** for the EDITH/JARVIS/FRIDAY project.

All implementation and team tasks should reference this document rather than independently redefining:

- Agent responsibilities
- Communication
- Permissions
- Memory
- Voice behavior
- Runtime responsibilities
- MVP scope

Changes to this architecture should be documented and agreed upon by the project team before they are treated as the new baseline.
