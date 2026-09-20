/** Small presentational helpers shared by the command-center UI. */

import type { EventType, TaskStatus } from "./types";

/** Format an ISO timestamp as a local HH:MM:SS, tolerating bad input. */
export function formatTime(iso: string | null): string {
  if (!iso) return "—";
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? "—" : d.toLocaleTimeString();
}

/** Human-readable label for an event type. */
export function eventLabel(type: EventType): string {
  const labels: Record<EventType, string> = {
    "task.created": "Task created",
    "task.queued": "Task queued",
    "task.started": "Task started",
    "agent.selected": "Agent selected",
    "agent.delegated": "Delegated",
    "agent.started": "Agent started",
    "tool.started": "Tool started",
    "tool.completed": "Tool completed",
    "agent.completed": "Agent completed",
    "task.completed": "Task completed",
    "task.failed": "Task failed",
  };
  return labels[type] ?? type;
}

export type StatusTone = "success" | "danger" | "progress" | "muted";

export function statusTone(status: TaskStatus): StatusTone {
  switch (status) {
    case "COMPLETED":
      return "success";
    case "FAILED":
      return "danger";
    case "CANCELLED":
      return "muted";
    default:
      return "progress"; // CREATED | QUEUED | RUNNING
  }
}

/** Whether a status is terminal (no further transitions expected). */
export function isTerminal(status: TaskStatus): boolean {
  return status === "COMPLETED" || status === "FAILED" || status === "CANCELLED";
}

// --- safe accessors for the free-form result payload ---------------------

export function asString(v: unknown): string | null {
  return typeof v === "string" ? v : null;
}

export function asArray(v: unknown): unknown[] | null {
  return Array.isArray(v) ? v : null;
}

export function asObject(v: unknown): Record<string, unknown> | null {
  return v && typeof v === "object" && !Array.isArray(v)
    ? (v as Record<string, unknown>)
    : null;
}
