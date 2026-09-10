const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export type CreateTaskRequest = {
  command: string;
};

export type TaskResponse = {
  task_id: string;
  status: string;
  message?: string;
};

export async function createTask(
  payload: CreateTaskRequest,
): Promise<TaskResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/tasks`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Failed to create task: ${response.status}`);
  }

  return response.json();
}

export async function getTask(taskId: string): Promise<TaskResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/tasks/${taskId}`, {
    method: "GET",
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch task: ${response.status}`);
  }

  return response.json();
}