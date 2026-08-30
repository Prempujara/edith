# ADR-006 — Voice Integration Strategy: Provider-Independent Adapter Boundary

**Author:** Mannan Shah (System Designer & Solutions Architect)  
**Date:** August 30, 2026  
**Status:** PROPOSED — REQUIRES TEAM APPROVAL  

---

## 1. Context
EDITH features voice command ingestion (STT) and spoken response playback (TTS). Paid voice SaaS providers (ElevenLabs, Amazon Polly, Google Speech) violate the **₹0 budget** rule. We require a reliable, free, and provider-independent voice integration architecture.

---

## 2. Decision
We establish **Provider-Independent Speech-to-Text (STT) and Text-to-Speech (TTS) Adapter Boundaries in `packages/voice`**. Client-side browser-native Web Speech APIs (`SpeechRecognition` for STT and `SpeechSynthesis` for TTS) may be evaluated as a zero-cost MVP implementation option.

---

## 3. Rationale
1. **Zero-Cost & Provider Independence:** Decouples core EDITH architecture from paid cloud voice services; client-side browser speech capabilities provide a zero-cost MVP option.
2. **Zero Server Load:** Client-side speech processing keeps backend server CPU usage low.
3. **Vendor Isolation:** Abstract interfaces in `packages/voice` ensure external voice providers (e.g. local Whisper or offline TTS engines) can be substituted seamlessly without touching core Orchestrator logic.

---

## 4. Consequences
* **Positive:** Zero financial cost, zero audio upload bandwidth to server, low implementation complexity.
* **Negative:** Voice recognition accuracy for the browser MVP option depends on browser engine and microphone hardware.
