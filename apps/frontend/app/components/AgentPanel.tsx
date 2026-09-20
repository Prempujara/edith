import type { AgentName, AgentResponse } from "@/lib/types";

// Accent per agent, purely cosmetic (not an API field).
const ACCENT: Record<AgentName, string> = {
  JARVIS: "text-cyan-300 border-cyan-400/30",
  EDITH: "text-violet-300 border-violet-400/30",
  FRIDAY: "text-amber-300 border-amber-400/30",
};

interface Props {
  agents: AgentResponse[] | null;
  loading: boolean;
  error: string | null;
}

export default function AgentPanel({ agents, loading, error }: Props) {
  return (
    <section className="rounded-xl border border-white/10 bg-white/[0.02] p-4">
      <h2 className="mb-3 text-xs font-semibold uppercase tracking-[0.2em] text-zinc-400">
        Agents
      </h2>

      {loading && <p className="text-sm text-zinc-500">Loading agents…</p>}

      {error && !loading && (
        <p className="text-sm text-red-300">{error}</p>
      )}

      {!loading && !error && agents?.length === 0 && (
        <p className="text-sm text-zinc-500">No agents registered.</p>
      )}

      <ul className="flex flex-col gap-3">
        {agents?.map((agent) => (
          <li
            key={agent.name}
            className={`rounded-lg border bg-black/20 p-3 ${ACCENT[agent.name] ?? "border-white/10 text-zinc-200"}`}
          >
            <div className="flex items-center justify-between">
              <span className="font-semibold tracking-wide">{agent.name}</span>
              {/* Reflects that the registry returned this agent; the API
                  exposes no per-agent status field, so we do not fake one. */}
              <span className="inline-flex items-center gap-1.5 text-[11px] text-emerald-300">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" aria-hidden />
                registered
              </span>
            </div>
            <p className="mt-1 text-xs text-zinc-400">{agent.role}</p>
            {agent.capabilities.length > 0 && (
              <ul className="mt-2 flex flex-wrap gap-1.5">
                {agent.capabilities.map((cap) => (
                  <li
                    key={cap}
                    className="rounded bg-white/5 px-1.5 py-0.5 font-mono text-[10px] text-zinc-300"
                  >
                    {cap}
                  </li>
                ))}
              </ul>
            )}
          </li>
        ))}
      </ul>
    </section>
  );
}
