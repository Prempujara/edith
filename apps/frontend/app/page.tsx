"use client";

import { useEffect, useState } from "react";

type Agent = {
  name: string;
  role: string;
  status: string;
  detail: string;
  color: string;
};

const agents: Agent[] = [
  {
    name: "JARVIS",
    role: "Reasoning & Coding",
    status: "THINKING",
    detail: "Planning task execution",
    color: "cyan",
  },
  {
    name: "EDITH",
    role: "Computer & Browser",
    status: "STANDBY",
    detail: "Ready for delegated actions",
    color: "violet",
  },
  {
    name: "FRIDAY",
    role: "Files & Organization",
    status: "STANDBY",
    detail: "Workspace indexed",
    color: "blue",
  },
];
const workflowActivities = [
  ["19:24:03", "JARVIS", "Analyzed user request", 0],
  ["19:24:05", "JARVIS", "Planning execution strategy", 10],
  ["19:24:08", "JARVIS", "Delegating browser task to EDITH", 35],
  ["19:24:11", "EDITH", "Opening project dashboard", 45],
  ["19:24:15", "EDITH", "Collecting requested information", 60],
  ["19:24:18", "FRIDAY", "Preparing result workspace", 75],
  ["19:24:21", "FRIDAY", "Organizing collected results", 90],
  ["19:24:24", "JARVIS", "Received final result", 100],
];



export default function Home() {
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [listening, setListening] = useState(false);
  const [activeAgent, setActiveAgent] = useState("JARVIS");

  useEffect(() => {
    if (!running) return;

    const timer = setInterval(() => {
      setProgress((current) => {
        if (current >= 100) {
          clearInterval(timer);
          setRunning(false);
          setActiveAgent("JARVIS");
          return 100;
        }

        if (current < 35) setActiveAgent("JARVIS");
        else if (current < 75) setActiveAgent("EDITH");
        else setActiveAgent("FRIDAY");

        return current + 5;
      });
    }, 350);

    return () => clearInterval(timer);
  }, [running]);

  const startDemo = () => {
    setProgress(0);
    setActiveAgent("JARVIS");
    setRunning(true);
  };
  const delegationMessage =
    progress < 35
      ? "JARVIS is analyzing the request"
      : progress < 75
        ? "JARVIS → EDITH  •  Delegating browser task"
        : progress < 100
          ? "EDITH → FRIDAY  •  Delegating result organization"
          : "FRIDAY → JARVIS  •  Final result returned";
  return (
    <main className="edith-shell">
      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />

      <header className="topbar">
        <div className="brand">
          <div className="brand-orb">E</div>
          <div>
            <div className="brand-name">EDITH</div>
            <div className="brand-subtitle">ENHANCED DISTRIBUTED INTELLIGENT TASK HANDLER</div>
          </div>
        </div>

        <div className="system-status">
          <span className="status-dot" />
          ALL SYSTEMS OPERATIONAL
        </div>

        <div className="topbar-time">19:24:18 IST</div>
      </header>

      <section className="dashboard">
        <aside className="sidebar panel">
          <div className="panel-label">AGENT NETWORK</div>

          <div className="agent-stack">
            {agents.map((agent) => (
              <div
                key={agent.name}
                className={`agent-card ${activeAgent === agent.name ? "active" : ""}`}
              >
                <div className={`agent-icon ${agent.color}`}>{agent.name[0]}</div>
                <div className="agent-info">
                  <div className="agent-name-row">
                    <strong>{agent.name}</strong>
                    <span>{activeAgent === agent.name && running ? "ACTIVE" : agent.status}</span>
                  </div>
                  <small>{agent.role}</small>
                  <p>{activeAgent === agent.name && running ? "Executing assigned task" : agent.detail}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="network-line">
            <span />
            <span />
            <span />
          </div>

          <div className="system-metrics">
            <div>
              <span>CPU</span>
              <strong>18%</strong>
            </div>
           <div>
              <span>MEMORY</span>
              <strong>42%</strong>
            </div>
            <div>
              <span>LATENCY</span>
              <strong>24ms</strong>
            </div>
          </div>
        </aside>

        <section className="main-column">
          <div className="hero panel">
            <div className="hero-copy">
              <span className="eyebrow">COMMAND CENTER</span>
              <h1>Good evening, Deev.</h1>
              <p>
                EDITH is standing by. Three intelligent agents are connected
                and ready to execute distributed tasks.
              </p>
            </div>

            <div className={`core ${running ? "core-running" : ""}`}>
              <div className="core-ring ring-one" />
              <div className="core-ring ring-two" />
              <div className="core-center">E</div>
              <span className="core-label">{running ? "PROCESSING" : "STANDBY"}</span>
            </div>
          </div>

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
                onClick={() => setListening((value) => !value)}
                aria-label="Toggle voice input"
              >
                <span className="mic-dot" />
                {listening ? "LISTENING..." : "VOICE"}
              </button>

              <div className="command-input">
                <span>{listening ? "Listening for command..." : "Enter a command for EDITH..."}</span>
                <span className="command-key">⌘ ↵</span>
              </div>

              <button className="execute-button" onClick={startDemo}>
                {running ? "RUNNING" : "RUN DEMO"}
              </button>
            </div>
          </div>

          <div className="lower-grid">
            <section className="panel task-panel">
              <div className="section-heading compact">
                <div>
                  <span className="eyebrow">CURRENT TASK</span>
                  <h2>Distributed Project Analysis</h2>
                </div>
                <span className="task-id">TASK-0042</span>
              </div>

              <div className="progress-track">
                <div className="progress-bar" style={{ width: `${progress}%` }} />
              </div>

              <div className="progress-meta">
                <span>{running ? "Agents executing workflow" : progress === 100 ? "Task completed" : "Awaiting execution"}</span>
                <strong>{progress}%</strong>
              </div>
              <div className="delegation-status">
  {delegationMessage}
</div>

              <div className="task-steps">
                <span className={progress >= 0 ? "done" : ""}>01&nbsp; PLAN</span>
                <span className={progress >= 35 ? "done" : ""}>02&nbsp; DELEGATE</span>
                <span className={progress >= 75 ? "done" : ""}>03&nbsp; EXECUTE</span>
                <span className={progress >= 100 ? "done" : ""}>04&nbsp; RESULT</span>
              </div>
            </section>

            <section className="panel activity-panel">
              <div className="section-heading compact">
                <div>
                  <span className="eyebrow">AGENT ACTIVITY</span>
                  <h2>Live Event Stream</h2>
                </div>
              </div>

              <div className="activity-list">
  {workflowActivities
    .filter(([, , , requiredProgress]) => progress >= requiredProgress)
    .map(([time, agent, event]) => (
      <div className="activity" key={`${time}-${agent}-${event}`}>
        <span className="activity-time">{time}</span>
        <span className="activity-agent">{agent}</span>
        <span>{event}</span>
      </div>
    ))}
</div>  
            </section>
          </div>
        </section>
      </section>

      <footer className="footer">
        <span>EDITH CORE v0.1 • MULTI-AGENT COMMAND SYSTEM</span>
        <span>JARVIS ↔ EDITH ↔ FRIDAY</span>
      </footer>
    </main>
  );
}
