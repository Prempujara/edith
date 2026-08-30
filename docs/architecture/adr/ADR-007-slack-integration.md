# ADR-007 — Slack Integration Strategy: Incoming Webhooks

**Author:** Mannan Shah (System Designer & Solutions Architect)  
**Date:** August 30, 2026  
**Status:** PROPOSED — REQUIRES TEAM APPROVAL  

---

## 1. Context
EDITH broadcasts task execution results to team Slack channels. We need a low-friction, zero-cost Slack integration that does not block core task execution or require paid Slack app infrastructure.

---

## 2. Decision
We implement a **Decoupled Event-Driven Slack Adapter (`packages/slack`)** consuming internal domain events (`task.completed`, `task.failed`) and dispatching formatted JSON block messages to a free **Slack Incoming Webhook URL**.

---

## 3. Reason
1. **Zero Financial Cost:** Incoming webhooks are a free, standard feature available in all free Slack workspaces.
2. **Decoupled Isolation:** The adapter listens to domain events asynchronously; a network error or invalid webhook URL will never delay or crash the Orchestrator.
3. **Simple Configuration:** Configured via a single environment variable (`SLACK_WEBHOOK_URL`). If missing, the adapter safely disables itself without throwing errors.

---

## 4. Consequences
* **Positive:** Zero cost, high fault isolation, simple setup.
* **Negative:** One-way notification only (does not support two-way interactive bot commands in MVP).
