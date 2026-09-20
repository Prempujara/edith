# EDITH System Architecture Documentation

**System Designer & Solutions Architect:** Mannan Shah  
**Project:** EDITH (Enhanced Distributed Intelligent Task Handler)  
**Date:** August 30, 2026 (Updated: September 20, 2026)  
**Status:** APPROVED ARCHITECTURE BASELINE  

---

## 1. Executive Overview

Welcome to the official **EDITH System Architecture Documentation**. This repository contains the complete technical architecture created by **Mannan Shah (Member 2)** to guide the multi-agent design, communication contracts, tool safety boundaries, and implementation reviews for the EDITH platform.

EDITH is a multi-agent AI task-handling ecosystem consisting of three specialized agents:
- **JARVIS** — Primary Conversational, Coding, Reasoning, and Research Specialist.
- **EDITH** — Computer & Browser Automation Specialist.
- **FRIDAY** — Files, Documents & Workspace Organization Specialist.

The architecture operates as a **Modular Monolith** under a strict **₹0 budget constraint**.

---

## 2. Architecture Documentation Sitemap

```text
docs/architecture/
├── README.md                              # Central Navigation Index (This File)
├── MANNAN-ARCHITECTURE-PROGRESS.md        # Member 2 Sprint Progress Tracker
├── system-architecture.md                 # System Blueprint & 3-Agent Ecosystem
├── agent-architecture.md                  # Agent Definitions, Matrix & Delegation Mechanics
├── communication.md                       # Task Lifecycle & Domain Event Contracts
├── tool-architecture.md                   # Tool Registry & Safety Sandboxing
├── shared-runtime-and-context.md          # Shared Runtime & Memory Architecture
├── integration-architecture.md            # Cloud/Local Trust Boundaries & Secrets Rules
├── architecture-review.md                 # Implementation Review of Current Codebase
├── architecture-gap-analysis.md           # Repository Baseline Gap Analysis
├── voice-architecture.md                  # Speech-to-Text & Text-to-Speech Adapters
├── slack-architecture.md                  # Event-Driven Slack Notification Adapter
├── error-failure-flow.md                  # Fault Isolation & Failure Recovery
├── mvp-vs-future.md                       # Zero-Budget MVP vs Future Extensions
├── diagrams/                              # Visual Mermaid Architecture Diagrams
│   ├── 01-overall-architecture.md         # Overall System Architecture
│   ├── 02-agent-communication.md          # Agent Communication & Delegation Sequence
│   ├── 03-task-lifecycle.md               # Task State Machine
│   ├── 04-trust-boundaries.md             # Hybrid Local / Cloud Trust Boundaries
│   ├── 05-tool-permissions.md             # Tool Sandboxing & Permission Pipeline
│   ├── 06-voice-pipeline.md               # Voice Ingestion & Playback Pipeline
│   └── 07-deployment-architecture.md      # MVP Deployment Architecture
└── adr/                                   # Architecture Decision Records
    ├── ADR-001-architecture-style.md      # Modular Monolith vs Microservices
    ├── ADR-002-communication-strategy.md  # Short HTTP Polling Strategy
    ├── ADR-003-orchestrator-boundary.md   # Agent Delegation & Shared Runtime Boundary
    ├── ADR-004-agent-tool-boundary.md     # Sandboxed Tool Execution Boundary
    ├── ADR-005-persistence-decision.md    # In-Memory Task Storage Strategy
    ├── ADR-006-voice-integration.md       # Provider-Independent Voice Strategy
    ├── ADR-007-slack-integration.md       # Decoupled Slack Webhook Adapter Strategy
    └── ADR-008-authentication-decision.md # Deferred Authentication Strategy
```

---

## 3. Quick Links to Core Architecture Documents

| Category | Primary Document | Description |
| :--- | :--- | :--- |
| **Progress Tracker** | [`MANNAN-ARCHITECTURE-PROGRESS.md`](file:///c:/Users/Mannan/OneDrive/Desktop/Edith/docs/architecture/MANNAN-ARCHITECTURE-PROGRESS.md) | Sprint 0-6 status tracking for Member 2. |
| **System Blueprint** | [`system-architecture.md`](file:///c:/Users/Mannan/OneDrive/Desktop/Edith/docs/architecture/system-architecture.md) | High-level system architecture and flow. |
| **Agent Ecosystem** | [`agent-architecture.md`](file:///c:/Users/Mannan/OneDrive/Desktop/Edith/docs/architecture/agent-architecture.md) | JARVIS, EDITH, and FRIDAY responsibilities and delegation rules. |
| **Task & Communication** | [`communication.md`](file:///c:/Users/Mannan/OneDrive/Desktop/Edith/docs/architecture/communication.md) | Task state machine, JSON schemas, and domain events. |
| **Tools & Security** | [`tool-architecture.md`](file:///c:/Users/Mannan/OneDrive/Desktop/Edith/docs/architecture/tool-architecture.md) | Permission levels, path locking, and command timeouts. |
| **Shared Runtime** | [`shared-runtime-and-context.md`](file:///c:/Users/Mannan/OneDrive/Desktop/Edith/docs/architecture/shared-runtime-and-context.md) | Shared Runtime vs Agent boundaries and memory model. |
| **Integrations & Secrets** | [`integration-architecture.md`](file:///c:/Users/Mannan/OneDrive/Desktop/Edith/docs/architecture/integration-architecture.md) | Trust boundaries, Slack, Web, and environment secrets rules. |
| **Code Review Report** | [`architecture-review.md`](file:///c:/Users/Mannan/OneDrive/Desktop/Edith/docs/architecture/architecture-review.md) | Findings and developer guidance for Prem & Deev. |
| **Visual Diagrams** | [`diagrams/`](file:///c:/Users/Mannan/OneDrive/Desktop/Edith/docs/architecture/diagrams) | 7 Mermaid architecture diagrams. |
| **ADR Suite** | [`adr/`](file:///c:/Users/Mannan/OneDrive/Desktop/Edith/docs/architecture/adr) | Architecture Decision Records (ADR 001 - 008). |

---

## 4. Architectural Core Directives

1. **Agents Decide Delegation:** JARVIS, EDITH, and FRIDAY inspect tasks and decide when delegation is required. The Shared Runtime coordinates message transport and task tracking.
2. **Zero-Budget Compliance:** Core EDITH functionality must operate without mandatory paid SaaS, cloud databases, or paid voice APIs.
3. **Controlled Tool Sandboxing:** File operations and subprocess shell executions must pass through workspace-checked Tool Sandbox boundaries.
4. **Decoupled Integrations:** Failure in external adapters (Slack notification, Web Speech API playback) MUST NOT fail a core task that executed successfully.
