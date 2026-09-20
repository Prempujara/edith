type Integration = {
  name: string;
  status: "CONNECTED" | "READY";
  detail: string;
};

const integrations: Integration[] = [
  {
    name: "GitHub",
    status: "CONNECTED",
    detail: "Repository access available",
  },
  {
    name: "Browser",
    status: "CONNECTED",
    detail: "Web automation ready",
  },
  {
    name: "Slack",
    status: "READY",
    detail: "Workspace integration ready",
  },
];

export default function IntegrationsPanel() {
  return (
    <section className="panel integrations-panel">
      <div className="section-heading compact">
        <div>
          <span className="eyebrow">INTEGRATIONS</span>
          <h2>Connected Services</h2>
        </div>
      </div>

      <div className="integration-list">
        {integrations.map((integration) => (
          <div className="integration-item" key={integration.name}>
            <div className="integration-info">
              <strong>{integration.name}</strong>
              <span>{integration.detail}</span>
            </div>

            <span className={`integration-status ${integration.status.toLowerCase()}`}>
              {integration.status}
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}
