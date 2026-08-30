# EDITH-001 — Slack Integration Architecture

**Author:** Mannan Shah (System Designer & Solutions Architect)  
**Project:** EDITH (Enhanced Distributed Intelligent Task Handler)  
**Date:** August 30, 2026  
**Status:** Proposed Specification — Subject to EDITH-000 Approval  

---

## 1. Overview

The Slack Integration Architecture defines how EDITH broadcasts task completion and failure alerts to Slack channels. The Slack integration is designed as a **decoupled, fire-and-forget event consumer** (`packages/slack`) operating under strict **₹0 budget constraints**.

---

## 2. Notification Flow Diagram

```mermaid
graph LR
    subgraph Core System
        EventBus[Internal Event Bus]
    end

    subgraph Slack Package [packages/slack]
        Subscriber[Slack Event Subscriber]
        Formatter[Message Block Formatter]
        HttpClient[Async HTTP Webhook Client]
    end

    subgraph External Slack Service
        WebhookEndpoint[Slack Incoming Webhook URL]
        SlackChannel[Slack Workspace Channel]
    end

    EventBus -->|Task Completion / Failure Event| Subscriber
    Subscriber --> Formatter
    Formatter -->|Formatted JSON Message Block| HttpClient
    HttpClient -->|Async POST Request| WebhookEndpoint
    WebhookEndpoint --> SlackChannel

    HttpClient -.->|Network Error / Timeout| ExceptionHandler[Catch & Log Warning - Core Task Unaffected]
```

---

## 3. Trigger Conditions & Notification Concept

Slack notifications are triggered exclusively upon terminal task states to prevent channel spam.

### 3.1 Trigger Events
* **Task Success:** Task Completion Event emitted by Orchestrator.
* **Task Failure:** Task Failure Event emitted by Orchestrator.

### 3.2 Notification Block Concept [PROPOSED]

#### Success Notification Block Concept
```json
{
  "text": "✅ EDITH Task Completed",
  "blocks": [
    {
      "type": "header",
      "text": { "type": "plain_text", "text": "✅ Task Completed Successfully" }
    },
    {
      "type": "section",
      "fields": [
        { "type": "mrkdwn", "text": "*Task ID:*\n9b1deb4d" },
        { "type": "mrkdwn", "text": "*Status:*\nCOMPLETED" }
      ]
    },
    {
      "type": "section",
      "text": { "type": "mrkdwn", "text": "*Summary:*\nTask completed successfully. All unit tests passed." }
    }
  ]
}
```

---

## 4. Credential Isolation & Environment Boundary

1. **Environment Configuration:** The Slack webhook URL is injected strictly via an environment variable (`SLACK_WEBHOOK_URL`).
2. **Disabled State Handling:** If `SLACK_WEBHOOK_URL` is unconfigured, missing, or set to placeholder, the `SlackAdapter` disables itself automatically during startup and logs an informational warning (`Slack notifications disabled: SLACK_WEBHOOK_URL not configured`).
3. **Secret Isolation:** Webhook credentials and tokens are excluded from source control (`.gitignore` enforces `.env` exclusion).

---

## 5. Failure Isolation & Quality Attributes

* **Non-Blocking Execution:** Slack notifications are dispatched asynchronously outside the main request/response loop.
* **Fault Isolation:** Network timeouts, invalid webhook URLs, or HTTP 5xx errors from Slack are caught cleanly by an internal exception handler. Webhook errors log a warning but **NEVER cause the core task status to fail**.
* **Zero-Budget Compliance:** Uses standard Slack Incoming Webhooks (a free feature in standard Slack workspaces). Requires zero paid bot subscriptions.
