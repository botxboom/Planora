"use client";

import { useState } from "react";

import { retryPlan } from "@/lib/api";
import { PlanState, RetryStrategy } from "@/lib/types";

const STRATEGIES: { id: RetryStrategy; label: string }[] = [
  { id: "auto", label: "Auto" },
  { id: "optimizer_agent", label: "Budget Optimizer" },
  { id: "transport_agent", label: "Transport Realism" },
  { id: "activity_agent", label: "Activity Completeness" },
  { id: "stay_agent", label: "Stay Quality" },
];

type Props = {
  runId: string;
  userId?: string;
  onNewPlan: (plan: PlanState) => void;
};

export function RetryControls({ runId, userId, onNewPlan }: Props) {
  const [strategy, setStrategy] = useState<RetryStrategy>("auto");
  const [status, setStatus] = useState("");

  async function handleRetry() {
    if (!runId) return;
    setStatus("Retrying...");
    try {
      const plan = await retryPlan({ runId, strategy, userId });
      onNewPlan(plan);
      setStatus("Retry completed.");
    } catch (error) {
      setStatus((error as Error).message);
    }
  }

  return (
    <div className="rounded-2xl border border-white/20 bg-white/80 p-4 backdrop-blur">
      <h3 className="text-sm font-semibold text-slate-700">Retry with focus</h3>
      <select
        value={strategy}
        onChange={(event) => setStrategy(event.target.value as RetryStrategy)}
        className="mt-2 w-full rounded-lg border border-slate-200 p-2 text-xs"
      >
        {STRATEGIES.map((item) => (
          <option key={item.id} value={item.id}>
            {item.label}
          </option>
        ))}
      </select>
      <button
        type="button"
        onClick={handleRetry}
        disabled={!runId}
        className="mt-3 rounded-full bg-indigo-600 px-4 py-2 text-xs font-semibold text-white disabled:opacity-50"
      >
        Retry Plan
      </button>
      {status && <p className="mt-2 text-xs text-slate-600">{status}</p>}
    </div>
  );
}
