import { StreamEnvelope } from "@/lib/types";

type SSEListener = (event: StreamEnvelope) => void;

function parseSSEChunk(chunk: string): StreamEnvelope[] {
  const events: StreamEnvelope[] = [];
  const blocks = chunk.split("\n\n").filter(Boolean);
  for (const block of blocks) {
    const lines = block.split("\n");
    let event = "node_completed";
    let dataText = "{}";
    for (const line of lines) {
      if (line.startsWith("event:")) {
        event = line.replace("event:", "").trim();
      } else if (line.startsWith("data:")) {
        dataText = line.replace("data:", "").trim();
      }
    }
    try {
      const data = JSON.parse(dataText) as Record<string, unknown>;
      events.push({ event: event as StreamEnvelope["event"], data });
    } catch {
      events.push({
        event: "error",
        data: { message: "Failed to parse SSE event payload." },
      });
    }
  }
  return events;
}

export async function consumeSSEStream(
  response: Response,
  listener: SSEListener,
): Promise<void> {
  if (!response.body) {
    throw new Error("Streaming response body is missing.");
  }
  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    if (!buffer.includes("\n\n")) continue;

    const splitIndex = buffer.lastIndexOf("\n\n");
    const consumable = buffer.slice(0, splitIndex);
    buffer = buffer.slice(splitIndex + 2);

    for (const parsed of parseSSEChunk(consumable)) {
      listener(parsed);
    }
  }
  if (buffer.trim().length > 0) {
    for (const parsed of parseSSEChunk(buffer)) {
      listener(parsed);
    }
  }
}
