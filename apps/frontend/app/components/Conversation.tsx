"use client";

import { useRef, useState } from "react";
import { submitCommand } from "@/lib/api";

type SpeechRecognitionEvent = Event & {
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
  onerror: (() => void) | null;
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
};

export default function Conversation({
  running,
  listening,
  activeAgent,
  onToggleVoice,
  onRunDemo,
}: ConversationProps) {
  const [command, setCommand] = useState("");
  const recognitionRef = useRef<SpeechRecognitionInstance | null>(null);

  const [submittedCommand, setSubmittedCommand] = useState(
    "Analyze the project status and prepare a summary.",
  );

  const handleSubmit = async () => {
    const trimmedCommand = command.trim();

    if (!trimmedCommand || running) return;

    setSubmittedCommand(trimmedCommand);
    setCommand("");

    try {
      const response = await submitCommand({
  command: trimmedCommand,
});

      console.log("EDITH task created:", response.task.task_id);

      onRunDemo();
    } catch (error) {
      console.error("Failed to submit command:", error);

      alert(
        "EDITH backend is unavailable. Please check that the backend is running.",
      );
    }
  };

  const handleToggleVoice = () => {
    if (listening) {
      recognitionRef.current?.stop();
      onToggleVoice();
      return;
    }

    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert("Speech recognition is not supported in this browser.");
      return;
    }

    const recognition = new SpeechRecognition();

    recognition.lang = "en-IN";
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setCommand(transcript);
    };

    recognition.onend = () => {
      onToggleVoice();
      recognitionRef.current = null;
    };

    recognition.onerror = () => {
      onToggleVoice();
      recognitionRef.current = null;
    };

    recognitionRef.current = recognition;
    onToggleVoice();
    recognition.start();
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
          <span className="eyebrow">CONVERSATION</span>
          <h2>Command Interface</h2>
        </div>

        <span className="connection">SECURE CHANNEL</span>
      </div>

      <div className="messages">
        <div className="message user-message">
          <span className="message-tag">YOU</span>
          <p>{submittedCommand}</p>
        </div>

        <div className="message edith-message">
          <span className="message-tag">EDITH</span>
          <p>
            Understood. JARVIS will coordinate the request and delegate
            external actions to the appropriate agents.
          </p>
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
        >
          <span className="mic-dot" />
          {listening ? "LISTENING..." : "VOICE"}
        </button>

        <div className="command-input">
          <input
            type="text"
            value={command}
            onChange={(event) => setCommand(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              listening
                ? "Listening for command..."
                : "Enter a command for EDITH..."
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