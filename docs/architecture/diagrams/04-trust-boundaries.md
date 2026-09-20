# Architecture Diagram 04 — Local / Cloud Trust Boundaries & Secrets Isolation

```mermaid
graph TD
    subgraph LocalTrust [LOCAL TRUST ZONE - HOST MACHINE]
        UserLocal([User & Desktop Environment])
        Dashboard[Next.js Local Web Dashboard]
        FastAPI[FastAPI Local Monolith Service]
        Runtime[Shared Runtime & Task Store]
        Tools[Tool Execution Sandbox]
        WorkspaceFS[(Project Workspace Filesystem)]
        LocalEnv[Uncommitted Local .env File]
    end

    subgraph Boundary [SECURITY & AGENT DELEGATION BOUNDARY]
        Sanitizer[Log & Payload Sanitizer]
        AuthCheck[API / Secret Sanitizer]
        PathCheck[Path Bounds Checker]
    end

    subgraph CloudTrust [EXTERNAL / CLOUD ZONE]
        CloudAI[External AI LLM APIs - Gemini / OpenAI]
        SlackCloud[Slack Workspace - Webhook Alert]
        ExternalWeb[Public Web Search Endpoints]
    end

    UserLocal <--> Dashboard
    Dashboard <--> FastAPI
    FastAPI <--> Runtime
    Runtime <--> Tools
    Tools <--> PathCheck
    PathCheck <--> WorkspaceFS

    LocalEnv -.->|Read Secrets at Startup| FastAPI
    LocalEnv -.->|Read API Keys| CloudAI

    Runtime --> Sanitizer
    Sanitizer -->|Sanitized HTTP Request| CloudAI
    Sanitizer -->|Sanitized Webhook Payload| SlackCloud
    Sanitizer -->|Search Query| ExternalWeb

    classDef local fill:#2d3748,stroke:#4a5568,color:#fff;
    classDef boundary fill:#742a2a,stroke:#9b2c2c,color:#fff;
    classDef cloud fill:#1a202c,stroke:#2d3748,color:#fff;

    class UserLocal,Dashboard,FastAPI,Runtime,Tools,WorkspaceFS,LocalEnv local;
    class Sanitizer,AuthCheck,PathCheck boundary;
    class CloudAI,SlackCloud,ExternalWeb cloud;
```

### Trust Boundary Safeguards
1. **Local Filesystem Isolation:** File tools cannot access paths outside `workspace_root`.
2. **Secrets Protection:** Keys stay in uncommitted `.env`. No credentials in Git logs or Markdown.
3. **Log Sanitization:** Sensitive tokens scrubbed before broadcasting to UI or Slack.
