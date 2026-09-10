type CurrentTaskProps = {
  progress: number;
  running: boolean;
  delegationMessage: string;
};

export default function CurrentTask({
  progress,
  running,
  delegationMessage,
}: CurrentTaskProps) {
  return (
    <section className="panel task-panel">
      <div className="section-heading compact">
        <div>
          <span className="eyebrow">CURRENT TASK</span>
          <h2>Distributed Project Analysis</h2>
        </div>

        <span className="task-id">TASK-0042</span>
      </div>

      <div className="progress-track">
        <div
          className="progress-bar"
          style={{ width: `${progress}%` }}
        />
      </div>

      <div className="progress-meta">
        <span>
          {running
            ? "Agents executing workflow"
            : progress === 100
              ? "Task completed"
              : "Awaiting execution"}
        </span>

        <strong>{progress}%</strong>
      </div>

      <div className="delegation-status">
        {delegationMessage}
      </div>

      <div className="task-steps">
        <span className={progress >= 0 ? "done" : ""}>
          01&nbsp; PLAN
        </span>

        <span className={progress >= 35 ? "done" : ""}>
          02&nbsp; DELEGATE
        </span>

        <span className={progress >= 75 ? "done" : ""}>
          03&nbsp; EXECUTE
        </span>

        <span className={progress >= 100 ? "done" : ""}>
          04&nbsp; RESULT
        </span>
      </div>
    </section>
  );
}