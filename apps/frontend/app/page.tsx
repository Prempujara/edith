"use client";

import { useEffect, useState } from "react";
import AgentNetwork from "./components/AgentNetwork";
import CommandCenter from "./components/CommandCenter";
import Conversation from "./components/Conversation";
import CurrentTask from "./components/CurrentTask";
import ActivityStream from "./components/ActivityStream";

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
            <div className="brand-subtitle">
              ENHANCED DISTRIBUTED INTELLIGENT TASK HANDLER
            </div>
          </div>
        </div>

        <div className="system-status">
          <span className="status-dot" />
          ALL SYSTEMS OPERATIONAL
        </div>

        <div className="topbar-time">19:24:18 IST</div>
      </header>

      <section className="dashboard">
        <AgentNetwork
          agents={agents}
          activeAgent={activeAgent}
          running={running}
        />

        <section className="main-column">
          <CommandCenter running={running} />

          <Conversation
            running={running}
            listening={listening}
            activeAgent={activeAgent}
            onToggleVoice={() => setListening((value) => !value)}
            onRunDemo={startDemo}
          />

          <div className="lower-grid">
            <CurrentTask
              progress={progress}
              running={running}
              delegationMessage={delegationMessage}
            />

            <ActivityStream
              progress={progress}
              workflowActivities={workflowActivities}
            />
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