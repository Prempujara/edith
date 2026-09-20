import { asArray, asObject, asString } from "@/lib/format";

/** Render a file-management / computer-control style plan (array of steps). */
function PlanList({ plan }: { plan: unknown[] }) {
  return (
    <ol className="mt-1 list-decimal space-y-1 pl-5 text-xs text-zinc-300">
      {plan.map((step, i) => (
        <li key={i}>{asString(step) ?? JSON.stringify(step)}</li>
      ))}
    </ol>
  );
}

/** Render key-value details object if present. */
function DetailsView({ details }: { details: Record<string, unknown> }) {
  return (
    <div className="mt-2 rounded-md border border-cyan-500/20 bg-cyan-950/20 p-2 font-mono text-xs text-cyan-200">
      <span className="font-semibold text-cyan-400 block mb-1">Execution Metrics:</span>
      <pre className="whitespace-pre-wrap overflow-x-auto text-[11px]">
        {JSON.stringify(details, null, 2)}
      </pre>
    </div>
  );
}

export default function ResultView({
  result,
  error,
}: {
  result: Record<string, unknown> | null;
  error: string | null;
}) {
  if (error) {
    return <p className="text-sm text-red-300">⚠️ {error}</p>;
  }
  if (!result) {
    return <p className="text-sm text-zinc-500">No result payload received.</p>;
  }

  // Unwrap delegation layer if present
  const isDelegation = result.kind === "delegation";
  const delegatedTo = asString(result.delegated_to);
  const activePayload = isDelegation && asObject(result.result) ? (result.result as Record<string, unknown>) : result;

  const agentName = asString(activePayload.agent) || delegatedTo || "JARVIS";
  const summary = asString(activePayload.summary) || asString(result.summary);
  const reply = asString(activePayload.reply);
  const code = asString(activePayload.code);
  const language = asString(activePayload.language) ?? "python";
  const plan = asArray(activePayload.plan);
  const details = asObject(activePayload.details);

  return (
    <div className="flex flex-col gap-3 rounded-lg border border-cyan-500/30 bg-black/50 p-4 shadow-lg">
      <div className="flex items-center justify-between border-b border-white/10 pb-2">
        <span className="text-xs font-semibold uppercase tracking-wider text-cyan-400">
          Agent Result • <span className="text-amber-300 font-bold">{agentName}</span>
        </span>
        {isDelegation && (
          <span className="rounded bg-amber-500/20 px-2 py-0.5 text-[10px] font-medium text-amber-300 border border-amber-500/30">
            DELEGATED WORKFLOW
          </span>
        )}
      </div>

      {summary && (
        <p className="text-sm font-medium text-zinc-100 bg-white/5 p-2 rounded border border-white/10">
          {summary}
        </p>
      )}

      {reply && <p className="text-sm text-zinc-200">{reply}</p>}

      {code && (
        <div className="mt-1">
          <span className="mb-1 block font-mono text-[10px] uppercase tracking-wider text-cyan-400">
            {language} Solution
          </span>
          <pre className="overflow-x-auto rounded-lg border border-cyan-500/30 bg-black/80 p-3 font-mono text-xs text-cyan-100">
            <code>{code}</code>
          </pre>
        </div>
      )}

      {plan && plan.length > 0 && (
        <div className="mt-1">
          <span className="text-xs font-semibold text-zinc-300">Action Plan & Execution Steps</span>
          <PlanList plan={plan} />
        </div>
      )}

      {details && <DetailsView details={details} />}

      <details className="mt-1">
        <summary className="cursor-pointer text-[11px] text-zinc-500 hover:text-zinc-300">
          Inspect Raw Payload
        </summary>
        <pre className="mt-1 overflow-x-auto rounded-lg border border-white/10 bg-black/60 p-3 font-mono text-[11px] text-zinc-400">
          {JSON.stringify(result, null, 2)}
        </pre>
      </details>
    </div>
  );
}
