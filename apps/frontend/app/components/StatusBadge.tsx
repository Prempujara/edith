import type { TaskStatus } from "@/lib/types";
import { statusTone } from "@/lib/format";

const TONE_CLASSES: Record<string, string> = {
  success: "border-emerald-500/40 bg-emerald-500/10 text-emerald-300",
  danger: "border-red-500/40 bg-red-500/10 text-red-300",
  progress: "border-amber-500/40 bg-amber-500/10 text-amber-300",
  muted: "border-zinc-500/40 bg-zinc-500/10 text-zinc-300",
};

export default function StatusBadge({ status }: { status: TaskStatus }) {
  const tone = statusTone(status);
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium tracking-wide ${TONE_CLASSES[tone]}`}
    >
      <span className="h-1.5 w-1.5 rounded-full bg-current" aria-hidden />
      {status}
    </span>
  );
}
