"use client";

import { useEffect, useRef, useState } from "react";
import { submitCommand, type TaskResponse } from "@/lib/api";
import ResultView from "./ResultView";

type SpeechRecognitionEvent = Event & {
  resultIndex: number;
  results: SpeechRecognitionResultList;
};

type SpeechRecognitionInstance = {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start: () => void;
  stop: () => void;
  onresult: ((event: SpeechRecognitionEvent) => void) | null;
  onend: (() => void) | null;
  onerror: ((event: { error: string }) => void) | null;
};

type SpeechRecognitionConstructor = new () => SpeechRecognitionInstance;

declare global {
  interface Window {
    SpeechRecognition?: SpeechRecognitionConstructor;
    webkitSpeechRecognition?: SpeechRecognitionConstructor;
  }
}

type ConversationProps = {
  running: boolean;
  listening: boolean;
  activeAgent: string;
  onToggleVoice: () => void;
  onRunDemo: () => void;
  onTaskExecuted?: (task: TaskResponse) => void;
};

export default function Conversation({
  running,
  listening,
  activeAgent,
  onToggleVoice,
  onRunDemo,
  onTaskExecuted,
}: ConversationProps) {
  const [command, setCommand] = useState("");
  const [voiceError, setVoiceError] = useState<string | null>(null);
  const [lastResponseSummary, setLastResponseSummary] = useState<string | null>(null);
  const [lastTaskResult, setLastTaskResult] = useState<Record<string, unknown> | null>(null);
  const recognitionRef = useRef<SpeechRecognitionInstance | null>(null);

  const [submittedCommand, setSubmittedCommand] = useState(
    "Analyze the project status and prepare a summary.",
  );

  const speakText = (text: string) => {
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      window.speechSynthesis.speak(utterance);
    }
  };

  const handleSubmit = async () => {
    const trimmedCommand = command.trim();

    if (!trimmedCommand || running) return;

    setSubmittedCommand(trimmedCommand);
    setCommand("");
    setVoiceError(null);

    try {
      const response = await submitCommand(trimmedCommand);
      console.log("EDITH task created:", response.task.id);

      setLastTaskResult(response.task.result);

      const summary =
        response.task.result?.summary ||
        `Task completed by ${response.task.assigned_agent}`;
      setLastResponseSummary(String(summary));
      speakText(String(summary));

      if (onTaskExecuted) {
        onTaskExecuted(response.task);
      } else {
        onRunDemo();
      }
    } catch (error) {
      console.error("Failed to submit command:", error);
      alert(
        "EDITH backend is unavailable. Please verify backend is running on http://127.0.0.1:8000.",
      );
    }
  };

  const handleToggleVoice = () => {
    setVoiceError(null);

    if (listening) {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      onToggleVoice();
      return;
    }

    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      const msg = "Speech recognition is not supported in this browser. Please use Chrome, Edge, or Safari.";
      setVoiceError(msg);
      alert(msg);
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.lang =
        typeof navigator !== "undefined" && navigator.language
          ? navigator.language
          : "en-US";
      recognition.continuous = false;
      recognition.interimResults = true;

      recognition.onresult = (event: SpeechRecognitionEvent) => {
        let transcript = "";
        for (let i = event.resultIndex; i < event.results.length; i++) {
          transcript += event.results[i][0].transcript;
        }
        if (transcript.trim()) {
          setCommand(transcript);
        }
      };

      recognition.onend = () => {
        onToggleVoice();
        recognitionRef.current = null;
      };

      recognition.onerror = (event) => {
        console.warn("Speech recognition error:", event.error);
        let errorMsg = "Voice input error.";
        if (event.error === "not-allowed") {
          errorMsg = "Microphone access blocked. Please allow mic permissions in browser settings.";
        } else if (event.error === "no-speech") {
          errorMsg = "No speech detected. Please try speaking again.";
        } else if (event.error === "audio-capture") {
          errorMsg = "No microphone hardware detected.";
        }
        setVoiceError(errorMsg);
        onToggleVoice();
        recognitionRef.current = null;
      };

      recognitionRef.current = recognition;
      onToggleVoice();
      recognition.start();
    } catch (err) {
      console.error("Failed to start speech recognition:", err);
      setVoiceError("Could not initialize microphone speech input.");
    }
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter") {
      handleSubmit();
    }
  };

  return (
    <div className="conversation panel">
      <div className="section-heading">
        <div>
          <span className="eyebrow">CONVERSATION & RESULTS</span>
          <h2>Command Interface</h2>
        </div>

        <span className="connection">SECURE CHANNEL</span>
      </div>

      {voiceError && (
        <div className="rounded border border-red-500/30 bg-red-500/10 p-2 text-xs text-red-300 mb-2">
          ⚠️ {voiceError}
        </div>
      )}

      <div className="messages">
        <div className="message user-message">
          <span className="message-tag">YOU</span>
          <p>{submittedCommand}</p>
        </div>

        <div className="message edith-message">
          <span className="message-tag">EDITH</span>
          <div className="flex flex-col gap-2 w-full">
            <p className="font-semibold text-cyan-300">
              {lastResponseSummary
                ? lastResponseSummary
                : "Understood. JARVIS will coordinate the request and delegate external actions to the appropriate agents."}
            </p>

            {lastTaskResult && (
              <div className="mt-2 border-t border-white/10 pt-2">
                <ResultView result={lastTaskResult} error={null} />
              </div>
            )}
          </div>
        </div>

        {running && (
          <div className="message thinking-message">
            <span className="message-tag">{activeAgent}</span>

            <p>
              {activeAgent === "JARVIS"
                ? "Planning execution strategy..."
                : activeAgent === "EDITH"
                  ? "Executing delegated computer task..."
                  : "Organizing collected results..."}
            </p>
          </div>
        )}
      </div>

      <div className="command-row">
        <button
          className={`voice-button ${listening ? "listening" : ""}`}
          onClick={handleToggleVoice}
          aria-label="Toggle voice input"
          title="Click to speak command"
        >
          <span className="mic-dot" />
          {listening ? "LISTENING..." : "🎙️ VOICE"}
        </button>

        <div className="command-input">
          <input
            type="text"
            value={command}
            onChange={(event) => setCommand(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              listening
                ? "Listening... Speak your command now"
                : "Enter a command for EDITH (e.g. 'Organize files', 'Open browser')..."
            }
            disabled={running}
            aria-label="Command input"
          />

          <span className="command-key">↵</span>
        </div>

        <button
          className="execute-button"
          onClick={handleSubmit}
          disabled={running || !command.trim()}
        >
          {running ? "RUNNING" : "SEND"}
        </button>

        <button
          className="execute-button"
          onClick={onRunDemo}
          disabled={running}
        >
          {running ? "RUNNING" : "RUN DEMO"}
        </button>
      </div>
    </div>
  );
}