import { consumeSSEStream } from "@/lib/sse";
import { FeedbackVote, PlanState, RetryStrategy, StreamEnvelope, UserRequest } from "@/lib/types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export async function streamPlan(
  request: UserRequest,
  onEvent: (event: StreamEnvelope) => void,
  signal?: AbortSignal,
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/plan/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
    signal,
  });
  if (!response.ok) {
    throw new Error(`Failed to start stream: ${response.status}`);
  }
  await consumeSSEStream(response, onEvent);
}

export async function submitFeedback(params: {
  runId: string;
  vote: FeedbackVote;
  userId?: string;
  comment?: string;
}): Promise<Record<string, unknown>> {
  const body: Record<string, string> = {
    run_id: params.runId,
    user_feedback: params.vote,
  };
  if (params.userId) body.user_id = params.userId;
  if (params.comment) body.comment = params.comment;

  const response = await fetch(`${API_BASE_URL}/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    throw new Error("Failed to submit feedback.");
  }
  return (await response.json()) as Record<string, unknown>;
}

export async function retryPlan(params: {
  runId: string;
  strategy: RetryStrategy;
  userId?: string;
}): Promise<PlanState> {
  const response = await fetch(`${API_BASE_URL}/plan/retry`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      run_id: params.runId,
      strategy: params.strategy,
      user_id: params.userId,
    }),
  });
  if (!response.ok) {
    throw new Error("Failed to retry plan.");
  }
  return (await response.json()) as PlanState;
}
