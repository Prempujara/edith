/**
 * Types mirroring the EDITH backend schemas (apps/backend/schemas/api.py).
 * These are transcribed from the FastAPI response models — not invented.
 */

export type AgentName = "JARVIS" | "EDITH" | "FRIDAY";

export type TaskStatus =
  | "CREATED"
  | "QUEUED"
  | "RUNNING"
  | "COMPLETED"
  | "FAILED"
  | "CANCELLED";

export type EventType =
  | "task.created"
  | "task.queued"
  | "task.started"
  | "agent.selected"
  | "agent.delegated"
  | "agent.started"
  | "tool.started"
  | "tool.completed"
  | "agent.completed"
  | "task.completed"
  | "task.failed";

export interface AgentResponse {
  name: AgentName;
  role: string;
  capabilities: string[];
}

export interface TaskResponse {
  id: string;
  parent_task_id: string | null;
  requester: string;
  assigned_agent: AgentName | null;
  input: string;
  status: TaskStatus;
  priority: number;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  /** Free-form result payload produced by the handling agent. */
  result: Record<string, unknown> | null;
  error: string | null;
}

export interface EventResponse {
  id: string;
  task_id: string;
  type: EventType;
  agent: AgentName | null;
  timestamp: string;
  payload: Record<string, unknown>;
}

export interface CommandResponse {
  task: TaskResponse;
}
