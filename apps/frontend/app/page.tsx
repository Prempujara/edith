"use client";

import { useEffect, useState } from "react";
import { getTaskEvents, submitCommand, type TaskResponse } from "@/lib/api";
import AgentNetwork from "./components/AgentNetwork";
import CommandCenter from "./components/CommandCenter";
import Conversation from "./components/Conversation";
import CurrentTask from "./components/CurrentTask";
import ActivityStream from "./components/ActivityStream";
import IntegrationsPanel from "./components/IntegrationsPanel";

type Agent = {
  name: string;
  role: string;
  status: string;
  detail: string;
  color: string;
};

export default function Home() {
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState(100);
  const [listening, setListening] = useState(false);
  const [activeAgent, setActiveAgent] = useState("JARVIS");
  const [currentTask, setCurrentTask] = useState<TaskResponse | null>(null);
  const [liveActivities, setLiveActivities] = useState<(string | number)[][]>([]);

  const [agents, setAgents] = useState<Agent[]>([
    {
      name: "JARVIS",
      role: "Reasoning & Coding",
      status: "STANDBY",
      detail: "Ready for user commands",
      color: "cyan",
    },
    {
      name: "EDITH",
      role: "Computer & Browser",
      status: "STANDBY",
      detail: "Ready for computer control",
      color: "violet",
    },
    {
      name: "FRIDAY",
      role: "Files & Organization",
      status: "STANDBY",
      detail: "Workspace ready",
      color: "blue",
    },
  ]);

  const handleTaskExecuted = async (task: TaskResponse) => {
    setCurrentTask(task);
    setRunning(true);
    setProgress(25);

    const targetAgent =
      (task.result?.delegated_to as string) ||
      task.assigned_agent ||
      "JARVIS";

    setActiveAgent("JARVIS");

    // Fetch real backend events
    try {
      const events = await getTaskEvents(task.id);
      const newActivities = events.map((ev: any) => {
        const timeStr = new Date().toLocaleTimeString();
        const agentName = ev.agent || "JARVIS";
        const typeStr = (ev.type || "event").replace(".", " ").toUpperCase();
        return [agentName, typeStr, timeStr];
      });
      setLiveActivities(newActivities);
    } catch (e) {
      console.warn("Could not fetch events:", e);
    }

    // Step animation simulating agent transition to target agent
    setTimeout(() => {
      setProgress(60);
      setActiveAgent(targetAgent);

      setAgents((prev) =>
        prev.map((a) => {
          if (a.name === targetAgent) {
            return { ...a, status: "EXECUTING", detail: `Processing task: ${task.input}` };
          }
          return { ...a, status: "STANDBY", detail: "Standing by" };
        })
      );
    }, 400);

    setTimeout(() => {
      setProgress(100);
      setRunning(false);
      setActiveAgent("JARVIS");

      setAgents([
        {
          name: "JARVIS",
          role: "Reasoning & Coding",
          status: "STANDBY",
          detail: "Task completed",
          color: "cyan",
        },
        {
          name: "EDITH",
          role: "Computer & Browser",
          status: "STANDBY",
          detail: targetAgent === "EDITH" ? "Browser/System action completed" : "Ready for actions",
          color: "violet",
        },
        {
          name: "FRIDAY",
          role: "Files & Organization",
          status: "STANDBY",
          detail: targetAgent === "FRIDAY" ? "Files organized" : "Workspace ready",
          color: "blue",
        },
      ]);
    }, 1200);
  };

  const startDemo = async () => {
    try {
      const res = await submitCommand("Write a Python function for factorial");
      handleTaskExecuted(res.task);
    } catch (err) {
      console.error("Demo submit error:", err);
    }
  };

  const delegationMessage = currentTask
    ? currentTask.result?.delegated_to
      ? `JARVIS → ${currentTask.result.delegated_to}  •  ${currentTask.result.summary || "Delegated task completed"}`
      : `JARVIS  •  ${currentTask.result?.summary || "Task executed directly"}`
    : "System ready • Enter a command to trigger agent execution";

  const [timeString, setTimeString] = useState<string>("");

  useEffect(() => {
    setTimeString(new Date().toLocaleTimeString());
    const interval = setInterval(() => {
      setTimeString(new Date().toLocaleTimeString());
    }, 1000);
    return () => clearInterval(interval);
  }, []);

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
          ALL AGENTS OPERATIONAL & CONNECTED TO BACKEND
        </div>

        <div className="topbar-time" suppressHydrationWarning>
          {timeString || "19:24:18 IST"}
        </div>
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
            onTaskExecuted={handleTaskExecuted}
          />

          <div className="lower-grid">
            <CurrentTask
              progress={progress}
              running={running}
              delegationMessage={delegationMessage}
            />

            <ActivityStream
              workflowActivities={liveActivities}
              running={running}
            />
            <IntegrationsPanel />
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