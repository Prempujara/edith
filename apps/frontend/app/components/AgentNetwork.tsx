"use client";

type Agent = {
  name: string;
  role: string;
  status: string;
  detail: string;
  color: string;
};

type AgentNetworkProps = {
  agents: Agent[];
  activeAgent: string;
  running: boolean;
};

export default function AgentNetwork({
  agents,
  activeAgent,
  running,
}: AgentNetworkProps) {
  return (
    <aside className="sidebar panel">
      <div className="panel-label">AGENT NETWORK</div>

      <div className="agent-stack">
        {agents.map((agent) => (
          <div
            key={agent.name}
            className={`agent-card ${
              activeAgent === agent.name ? "active" : ""
            }`}
          >
            <div className={`agent-icon ${agent.color}`}>
              {agent.name[0]}
            </div>

            <div className="agent-info">
              <div className="agent-name-row">
                <strong>{agent.name}</strong>
                <span>
                  {activeAgent === agent.name && running
                    ? "ACTIVE"
                    : agent.status}
                </span>
              </div>

              <small>{agent.role}</small>

              <p>
                {activeAgent === agent.name && running
                  ? "Executing assigned task"
                  : agent.detail}
              </p>
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
  );
}