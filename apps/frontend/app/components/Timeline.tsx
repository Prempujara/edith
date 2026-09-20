import type { EventResponse } from "@/lib/types";
import { asString, eventLabel, formatTime } from "@/lib/format";

/** Derive a short human detail line from an event's payload, if any. */
function detail(ev: EventResponse): string | null {
  const p = ev.payload ?? {};
  const target = asString(p.target_agent);
  const capability = asString(p.capability);
  if (ev.type === "agent.selected") {
    const handled = p.handled_directly === true;
    if (capability && handled) return `${capability} → handled by JARVIS`;
    if (capability && target) return `${capability} → ${target}`;
    return capability ?? null;
  }
  if (ev.type === "agent.delegated" && target) {
    return `JARVIS → ${target}`;
  }
  return null;
}

export default function Timeline({ events }: { events: EventResponse[] }) {
  if (events.length === 0) {
    return <p className="text-xs text-zinc-500">No events recorded.</p>;
  }
  return (
    <ol className="relative flex flex-col gap-2 border-l border-white/10 pl-4">
      {events.map((ev) => {
        const d = detail(ev);
        return (
          <li key={ev.id} className="relative">
            <span
              className="absolute -left-[21px] top-1.5 h-2 w-2 rounded-full bg-cyan-400/70 ring-2 ring-black"
              aria-hidden
            />
            <div className="flex flex-wrap items-baseline gap-x-2 gap-y-0.5">
              <span className="text-sm text-zinc-200">{eventLabel(ev.type)}</span>
              {ev.agent && (
                <span className="rounded bg-white/5 px-1.5 py-0.5 font-mono text-[10px] text-zinc-400">
                  {ev.agent}
                </span>
              )}
              <span className="ml-auto font-mono text-[10px] text-zinc-500">
                {formatTime(ev.timestamp)}
              </span>
            </div>
            {d && <p className="mt-0.5 text-xs text-cyan-300/80">{d}</p>}
          </li>
        );
      })}
    </ol>
  );
}
