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
          <p>Analyze the project status and prepare a summary.</p>
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
          <span>
            {listening
              ? "Listening for command..."
              : "Enter a command for EDITH..."}
          </span>

          <span className="command-key">⌘ ↵</span>
        </div>

        <button className="execute-button" onClick={onRunDemo}>
          {running ? "RUNNING" : "RUN DEMO"}
        </button>
      </div>
    </div>
  );
}