import { StreamEnvelope } from "@/lib/types";

/**
 * Maps SSE / graph events to short, user-friendly status copy (no internal jargon).
 */
export function getFriendlyStatus(
  lastEvent: StreamEnvelope | null,
  isStreaming: boolean,
): string {
  if (!isStreaming) {
    return "";
  }

  if (!lastEvent) {
    return "Planning your trip…";
  }

  switch (lastEvent.event) {
    case "run_started":
      return "Planning your trip…";
    case "planner_completed":
      return "Understanding what matters to you…";
    case "agent_completed": {
      const node = String(lastEvent.data.node ?? "");
      if (node === "transport_agent") {
        return "Finding the best way to get there…";
      }
      if (node === "stay_agent") {
        return "Choosing stays that fit your trip…";
      }
      if (node === "activity_agent") {
        return "Finding great places and experiences…";
      }
      if (node === "optimizer_agent") {
        return "Analyzing your budget…";
      }
      return "Shaping your itinerary…";
    }
    case "aggregator_completed":
      return "Assembling your itinerary…";
    case "judge_completed":
      return "Making sure everything works together…";
    case "retry_triggered":
      return "Polishing the details…";
    case "final_result":
      return "Here’s your trip.";
    case "error":
      return "Something went wrong. Please try again.";
    default:
      return "Planning your trip…";
  }
}
