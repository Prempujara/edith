# ADR-007 — Slack Integration Strategy: Incoming Webhook Adapter

**Author:** Mannan Shah (System Designer & Solutions Architect)  
**Date:** August 30, 2026  
**Status:** PROPOSED — REQUIRES TEAM APPROVAL  

---

## 1. Context
EDITH broadcasts task execution results to team Slack channels. We need a low-friction, zero-cost Slack integration that does not block core task execution or require paid Slack app infrastructure.

---

## 2. Decision
We implement a **Decoupled Event-Driven Slack Notification Adapter (`packages/slack`)** consuming internal domain events (Task Completion and Failure events) and dispatching formatted message blocks to a zero-cost **Slack Incoming Webhook URL**.

---

## 3. Rationale
1. **Zero Financial Cost:** Incoming webhooks are a free feature available in standard Slack workspaces.
2. **Decoupled Isolation:** The adapter listens to domain events asynchronously; a network error or invalid webhook URL will never delay the Orchestrator or cause a successful task to fail.
3. **Simple Configuration:** Configured via an environment variable (`SLACK_WEBHOOK_URL`). If missing, the adapter safely disables itself without throwing runtime errors.

---

## 4. Consequences
* **Positive:** Zero cost, high fault isolation, simple setup.
* **Negative:** One-way notification only (does not support two-way interactive bot commands in MVP).
