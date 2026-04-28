"use client";

import { motion } from "framer-motion";

import { StreamEnvelope } from "@/lib/types";

type Props = { events: StreamEnvelope[] };

function labelForEvent(event: StreamEnvelope): string {
  switch (event.event) {
    case "run_started":
      return "Run started";
    case "planner_completed":
      return "Planner parsed constraints";
    case "agent_completed":
      return `Agent completed: ${String(event.data.node ?? "unknown")}`;
    case "judge_completed":
      return "Judge evaluated itinerary";
    case "retry_triggered":
      return "Retry triggered from judge feedback";
    case "final_result":
      return "Final itinerary ready";
    case "error":
      return `Error: ${String(event.data.message ?? "unknown")}`;
    default:
      return event.event;
  }
}

export function PlanProgressTimeline({ events }: Props) {
  return (
    <div className="rounded-2xl border border-white/20 bg-white/80 p-4 backdrop-blur">
      <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-600">
        Live Progress
      </h3>
      <div className="space-y-2">
        {events.length === 0 && (
          <p className="text-sm text-slate-500">No stream events yet.</p>
        )}
        {events.map((event, index) => (
          <motion.div
            key={`${event.event}-${index}`}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            className="rounded-lg border border-slate-100 bg-white px-3 py-2 text-xs text-slate-700"
          >
            {labelForEvent(event)}
          </motion.div>
        ))}
      </div>
    </div>
  );
}
