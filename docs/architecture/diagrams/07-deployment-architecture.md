# Architecture Diagram 07 — MVP Deployment & Development Architecture

```mermaid
graph TD
    subgraph DeveloperMachine [LOCAL DEVELOPER ENVIRONMENT - ZERO-BUDGET HOST]
        
        subgraph FrontendContainer [Frontend Dev Server]
            NextServer[Next.js Dev Server - Node.js]
            NextPort[Port 3000]
        end

        subgraph BackendContainer [Backend FastAPI Server]
            UvicornServer[Uvicorn Server - Python 3.11+]
            FastAPIPort[Port 8000]
            
            subgraph MonolithCore [FastAPI Modular Monolith Process]
                AgentsPackage[Agents Tier - JARVIS / EDITH / FRIDAY]
                RuntimePackage[Shared Runtime Package]
                ToolSandbox[Tool Sandbox Package]
                InMemoryStore[In-Memory Task State Store]
            end
        end

        subgraph HostOS [Host OS Resources]
            TargetFS[(Project Workspace File System)]
            LocalGit[Local Git Binary]
            LocalBrowser[Host Web Browser / Playwright]
        end
    end

    BrowserUser([User Browser]) <--> NextPort
    NextPort -->|Proxied REST API Requests / Short Polling| FastAPIPort
    FastAPIPort <--> MonolithCore
    MonolithCore <--> TargetFS
    MonolithCore <--> LocalGit
    MonolithCore <--> LocalBrowser
```

### Deployment Properties
- **Zero Cost:** No paid cloud servers, databases, or container orchestration services.
- **Single Process Monolith:** Backend components run inside a single Python process managed by `uvicorn`.
- **Development Simplicity:** Live hot-reloading for both Next.js and FastAPI.
