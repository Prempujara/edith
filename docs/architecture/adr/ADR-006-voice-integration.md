# ADR-006 — Voice Integration Strategy: Browser Web Speech API

**Author:** Mannan Shah (System Designer & Solutions Architect)  
**Date:** August 30, 2026  
**Status:** PROPOSED — REQUIRES TEAM APPROVAL  

---

## 1. Context
EDITH features voice command ingestion (STT) and spoken response playback (TTS). Paid voice SaaS providers (ElevenLabs, Amazon Polly, Google Speech) violate the **₹0 budget** rule. We require a reliable, free, and provider-independent voice integration architecture.

---

## 2. Decision
We standardize on client-side **Browser-Native Web Speech APIs (`SpeechRecognition` for STT and `SpeechSynthesis` for TTS)**, wrapped behind clean provider-agnostic interfaces in `packages/voice`.

---

## 3. Reason
1. **100% Free & Unlimited:** Built directly into modern web browsers (Chrome, Edge, Safari); zero API subscription fees or rate limits.
2. **Zero Server Load:** Speech recognition and synthesis run on the client device, keeping backend server CPU usage low.
3. **Vendor Isolation:** Abstract interfaces in `packages/voice` ensure external voice providers (local Whisper or gTTS) can be substituted seamlessly if required.

---

## 4. Consequences
* **Positive:** Zero financial cost, zero audio upload latency over network, low implementation complexity.
* **Negative:** Voice recognition quality depends on client browser engine and microphone hardware.
