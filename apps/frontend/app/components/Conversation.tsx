"use client";

import { useState } from "react";

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
  const [submittedCommand, setSubmittedCommand] = useState(
    "Analyze the project status and prepare a summary.",
  );

  const handleSubmit = () => {
    const trimmedCommand = command.trim();

    if (!trimmedCommand || running) return;

    setSubmittedCommand(trimmedCommand);
    setCommand("");
    onRunDemo();
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
          onClick={onToggleVoice}
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