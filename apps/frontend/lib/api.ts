const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export type CommandRequest = {
  command: string;
};

export type TaskResponse = {
  id: string;
  parent_task_id: string | null;
  requester: string;
  assigned_agent: string | null;
  input: string;
  status: string;
  priority: number;
  created_at: string;
  queued_at: string | null;
  started_at: string | null;
  completed_at: string | null;
  result: Record<string, unknown> | null;
  error: Record<string, unknown> | null;
};

export type CommandResponse = {
  task: TaskResponse;
};

export async function submitCommand(
  payload: CommandRequest,
): Promise<CommandResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/commands`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Failed to submit command: ${response.status}`);
  }

  return response.json();
}

export async function getTask(taskId: string): Promise<TaskResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/tasks/${taskId}`,
    {
      method: "GET",
      cache: "no-store",
    },
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch task: ${response.status}`);
  }

  return response.json();
}

export async function getTaskEvents(
  taskId: string,
): Promise<Record<string, unknown>[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/tasks/${taskId}/events`,
    {
      method: "GET",
      cache: "no-store",
    },
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch task events: ${response.status}`);
  }

  return response.json();
}