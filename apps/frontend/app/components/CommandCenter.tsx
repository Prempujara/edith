type CommandCenterProps = {
  running: boolean;
};

const systemStatus = [
  ["API", "ONLINE"],
  ["AGENTS", "ONLINE"],
  ["EVENTS", "STREAMING"],
];

const getGreeting = () => {
  const hour = new Date().getHours();
  if (hour < 12) return "Good morning, Prem.";
  if (hour < 18) return "Good afternoon, Prem.";
  return "Good evening, Prem.";
};

export default function CommandCenter({ running }: CommandCenterProps) {
  return (
    <div className="hero panel">
      <div className="hero-copy">
        <span className="eyebrow">COMMAND CENTER</span>

        <h1 suppressHydrationWarning>{getGreeting()}</h1>

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