# Architecture Diagram 06 — Voice Pipeline Architecture

```mermaid
graph LR
    subgraph STTPipeline [Voice Command Ingestion Pipeline]
        Mic([User Microphone]) --> BrowserSTT[Browser Web Speech API - SpeechRecognition]
        BrowserSTT --> TranscribedText[Transcribed Text String]
        TranscribedText --> DashboardUI[Next.js Dashboard Input Form]
    end

    subgraph AgentPipeline [Agent Execution Pipeline]
        DashboardUI --> API[FastAPI Gateway]
        API --> JARVIS[JARVIS Agent Reasoning & Tools]
        JARVIS --> TaskResult[Task Result Summary Payload]
    end

    subgraph TTSPipeline [Voice Response Playback Pipeline]
        TaskResult --> EventBus[Async Event Broker]
        EventBus --> BrowserTTS[Browser Web Speech API - SpeechSynthesis]
        BrowserTTS --> Speaker([User Speaker])
    end

    subgraph FallbackModel [Zero-Budget & Headless Fallbacks]
        TextForm[Direct Text Keyboard Input] -.->|Fallback if STT unsupported| DashboardUI
        SilentLogs[Dashboard Visual Activity Log] -.->|Fallback if TTS muted| Speaker
    end
```

### Voice Pipeline Design
1. **Client-Side STT:** Zero-cost speech capture via standard browser APIs.
2. **Asynchronous Agent Execution:** Prompt processes through normal agent pipelines.
3. **Decoupled TTS Playback:** Completion events trigger speech playback without blocking API responses.
