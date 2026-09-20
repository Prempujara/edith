# EDITH-001 — Integration & Cloud / Local Trust Architecture

**Author:** Mannan Shah (System Designer & Solutions Architect)  
**Project:** EDITH (Enhanced Distributed Intelligent Task Handler)  
**Date:** September 20, 2026  
**Status:** APPROVED ARCHITECTURE BASELINE  

---

## 1. System Integration Overview

EDITH integrates with external services, host tools, and browser interfaces. Every integration is decoupled via abstract adapter interfaces to satisfy **Rule 4 (Zero-Budget)** and ensure zero vendor lock-in.

```
┌─────────────────────────────────────────────────────────────┐
│                         LOCAL TRUST                         │
│                      (Host Machine)                         │
│  • Local Filesystem   • Git CLI      • Terminal / Shell     │
│  • Desktop OS GUI     • Local Memory • FastAPI Runtime      │
└──────────────────────────────┬──────────────────────────────┘
                               │ Decoupled Adapters
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                        EXTERNAL TRUST                       │
│                      (Optional Cloud)                       │
│  • Cloud LLM APIs (Gemini/OpenAI) • Slack Incoming Webhook  │
│  • Web Search Endpoints           • External Git Remotes    │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Integration Matrix

| Integration | Direction | Local vs External | Zero-Budget Strategy | Secrets & Credentials Handling | Failure Behavior |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **GitHub / Git** | Bi-directional | Local CLI / Remote HTTP | Local `git` binary + Personal Access Token. | Read from `GITHUB_TOKEN` in local `.env`. Never committed. | Tool raises `GitExecutionError`; task logs warning. |
| **Slack Notifications** | Outbound | External Cloud Webhook | Free Slack Incoming Webhook URL. | Read from `SLACK_WEBHOOK_URL` in local `.env`. | Non-fatal: Webhook error logged silently, task completes normally. |
| **Web Search & Browsing** | Outbound | External Web | Free tier web search API or direct HTTP scrapers. | Optional API key in `.env`. | Tool returns empty search array; agent uses local knowledge. |
| **Desktop / Browser Control** | Local Action | Local Host OS | Open-source Python automation libraries (`playwright` / `pyautogui`). | No credentials required. | Tool captures screenshot error; returns failure to EDITH agent. |
| **AI Model Provider** | Outbound HTTP | External API / Local LLM | Local Ollama / Llama.cpp or free-tier Gemini / OpenAI API keys. | API keys stored in local `.env`. | LLM Provider interface attempts fallback model; raises `LLMProviderError`. |
| **Voice Interface** | Inbound/Outbound | Client Browser | Browser Web Speech API (`SpeechRecognition` / `SpeechSynthesis`). | No credentials required. | UI falls back to manual text input mode. |

---

## 3. Trust Boundaries & Credentials Security Rules

### 3.1 Strict Credentials Rules
1. **Zero Hardcoded Credentials:** API keys, webhook URLs, and access tokens MUST NEVER be committed to Git repositories or hardcoded in source code or Markdown examples.
2. **Environment File Isolation:** All secrets must be loaded dynamically from an uncommitted `.env` file via Python `pydantic-settings` or `os.environ`.
3. **Log Sanitization:** Event emission and terminal logger layers MUST scrub key patterns (e.g. `sk-`, `ghp_`, `https://hooks.slack.com`) prior to output.

### 3.2 Failure Isolation Hierarchy
Optional integrations (Slack, Voice playback, secondary web search) MUST operate under an isolated try-except wrapper. A network failure in Slack or a missing voice synthesis voice MUST NOT fail a core task that executed successfully.
