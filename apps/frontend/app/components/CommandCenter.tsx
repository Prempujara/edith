type CommandCenterProps = {
  running: boolean;
};

const systemStatus = [
  ["API", "ONLINE"],
  ["AGENTS", "ONLINE"],
  ["EVENTS", "STREAMING"],
];

export default function CommandCenter({ running }: CommandCenterProps) {
  return (
    <div className="hero panel">
      <div className="hero-copy">
        <span className="eyebrow">COMMAND CENTER</span>

        <h1>Good evening, Deev.</h1>

        <p>
          EDITH is standing by. Three intelligent agents are connected
          and ready to execute distributed tasks.
        </p>

        <div className="system-status">
          {systemStatus.map(([label, status]) => (
            <div className="system-status-item" key={label}>
              <span className="status-dot" />
              <span>{label}</span>
              <strong>{status}</strong>
            </div>
          ))}
        </div>
      </div>

      <div className={`core ${running ? "core-running" : ""}`}>
        <div className="core-ring ring-one" />
        <div className="core-ring ring-two" />
        <div className="core-center">E</div>

        <span className="core-label">
          {running ? "PROCESSING" : "STANDBY"}
        </span>
      </div>
    </div>
  );
}