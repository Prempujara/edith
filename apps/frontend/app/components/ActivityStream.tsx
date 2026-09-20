type ActivityStreamProps = {
  workflowActivities: (string | number)[][];
  running: boolean;
};

export default function ActivityStream({
  workflowActivities,
  running,
}: ActivityStreamProps) {
  const integrationActivities = [
    ["GITHUB", "Repository connected", "ready"],
    ["BROWSER", "Browser automation ready", "ready"],
    ["SLACK", "Workspace integration ready", "ready"],
  ];

  const activities = [
    ...workflowActivities,
    ...integrationActivities,
  ];

  return (
    <section className="panel activity-panel">
      <div className="section-heading compact">
        <div>
          <span className="eyebrow">AGENT ACTIVITY</span>
          <h2>Live Event Stream</h2>
        </div>
      </div>

      <div className="activity-list">
        {activities.map(([agent, event, time]) => (
          <div className="activity" key={`${agent}-${event}-${time}`}>
            <span className="activity-time">{time}</span>
            <span className="activity-agent">{agent}</span>
            <span>{event}</span>
          </div>
        ))}
      </div>

      {!running && workflowActivities.length === 0 && (
        <div className="activity-empty">
          Waiting for agent activity...
        </div>
      )}
    </section>
  );
}