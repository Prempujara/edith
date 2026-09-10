type ActivityStreamProps = {
  progress: number;
  workflowActivities: (string | number)[][];
};

export default function ActivityStream({
  progress,
  workflowActivities,
}: ActivityStreamProps) {
  return (
    <section className="panel activity-panel">
      <div className="section-heading compact">
        <div>
          <span className="eyebrow">AGENT ACTIVITY</span>
          <h2>Live Event Stream</h2>
        </div>
      </div>

      <div className="activity-list">
        {workflowActivities
          .filter(([, , , requiredProgress]) => progress >= Number(requiredProgress))
          .map(([time, agent, event]) => (
            <div
              className="activity"
              key={`${time}-${agent}-${event}`}
            >
              <span className="activity-time">{time}</span>
              <span className="activity-agent">{agent}</span>
              <span>{event}</span>
            </div>
          ))}
      </div>
    </section>
  );
}