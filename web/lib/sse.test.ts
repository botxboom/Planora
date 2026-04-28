import { describe, expect, it } from "vitest";

import { consumeSSEStream } from "./sse";

function createStreamResponse(payload: string): Response {
  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    start(controller) {
      controller.enqueue(encoder.encode(payload));
      controller.close();
    },
  });
  return new Response(stream, { headers: { "Content-Type": "text/event-stream" } });
}

describe("consumeSSEStream", () => {
  it("parses SSE events into envelopes", async () => {
    const response = createStreamResponse(
      "event: run_started\ndata: {\"run_id\":\"abc\"}\n\n" +
        "event: final_result\ndata: {\"result\":{\"ok\":true}}\n\n",
    );
    const events: Array<{ event: string }> = [];
    await consumeSSEStream(response, (event) => events.push(event));
    expect(events).toHaveLength(2);
    expect(events[0].event).toBe("run_started");
    expect(events[1].event).toBe("final_result");
  });
});
