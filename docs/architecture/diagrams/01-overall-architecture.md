# Architecture Diagram 01 — Overall System Architecture

```mermaid
graph TD
    User([User])
    
    subgraph Frontend [User Facing Layer]
        WebUI[Next.js Dashboard]
        VoiceIn[Voice STT Ingestion]
        SlackClient[Slack Workspace Channel]
    end
    
    subgraph Gateway [API Layer - FastAPI]
        API[FastAPI Gateway REST Endpoints]
    end
    
    subgraph Agents [Specialized Agent Tier]
        JARVIS[JARVIS Agent - Primary / Coding / Research]
        EDITH[EDITH Agent - Computer / Browser Control]
        FRIDAY[FRIDAY Agent - Files / Organization]
    end
    
    subgraph Runtime [Shared Agent Runtime]
        TaskTracker[Task Lifecycle Tracker]
        EventBus[In-Process Event Bus]
        ContextStore[Shared Memory & Context]
        ToolRegistry[Tool Safety Registry]
    end
    
    subgraph Sandbox [Tool Execution Sandbox]
        FileTool[File Operations Tool]
        ShellTool[Shell Execution Tool]
        BrowserTool[Browser GUI Tool]
        GitTool[Git Repository Tool]
    end
    
    subgraph OutputAdapters [Output Adapters]
        VoiceOut[Voice TTS Adapter]
        SlackOut[Slack Notification Webhook]
    end
    
    User -->|Text Prompt| WebUI
    User -->|Voice Command| VoiceIn
    VoiceIn -->|Recognized Text| WebUI
    SlackClient -->|Channel Alert| User

    WebUI -->|POST /api/v1/tasks| API
    API -->|1. Register Task| TaskTracker
    API -->|2. Dispatch Request| JARVIS

    JARVIS -->|3a. Direct Tool Execution| ToolRegistry
    JARVIS -->|3b. Delegate Computer Subtask| EDITH
    JARVIS -->|3c. Delegate Filing Subtask| FRIDAY

    EDITH -->|4a. Computer Control Request| ToolRegistry
    FRIDAY -->|4b. File System Request| ToolRegistry

    ToolRegistry -->|Permission Check| FileTool
    ToolRegistry -->|Permission Check| ShellTool
    ToolRegistry -->|Permission Check| BrowserTool
    ToolRegistry -->|Permission Check| GitTool

    FileTool -->|Execution Result| TaskTracker
    ShellTool -->|Execution Result| TaskTracker
    BrowserTool -->|Execution Result| TaskTracker
    GitTool -->|Execution Result| TaskTracker

    TaskTracker -->|Emit State Event| EventBus
    EventBus -->|Progress Update| WebUI
    EventBus -->|Task Completion Alert| VoiceOut
    EventBus -->|Task Completion Alert| SlackOut

    VoiceOut -->|Audio Playback| User
    SlackOut -->|Webhook Message| SlackClient
```

### Key Elements
- **User Interface:** Web Dashboard and browser Web Speech STT.
- **JARVIS:** Primary conversational entry point and decision-maker for agent delegation.
- **EDITH & FRIDAY:** Domain specialists delegated to by JARVIS.
- **Shared Runtime:** Coordinates transport, task state, events, memory, and permissions.
- **Tool Sandbox:** Enforces path boundaries and command execution safety.
