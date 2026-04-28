"use client";

import { PlanState } from "@/lib/types";

type Props = { plan: PlanState | null };

export function JudgeScoreCard({ plan }: Props) {
  const judge = plan?.judge_output;
  const budgetSummary = plan?.final_itinerary?.budget_summary;

  return (
    <div className="flex overflow-hidden rounded-2xl bg-white shadow-card ring-1 ring-black/5">
      <div className="flex w-28 shrink-0 flex-col justify-center bg-brand-orange px-4 py-6 text-center text-white md:w-32">
        <p className="text-[10px] font-bold uppercase tracking-widest text-white/90">
          Score
        </p>
        <p className="mt-1 text-4xl font-bold tabular-nums leading-none md:text-5xl">
          {judge?.score != null ? judge.score : "—"}
        </p>
        <p className="mt-1 text-xs font-medium text-white/80">out of 10</p>
      </div>
      <div className="min-w-0 flex-1 px-5 py-5 text-brand-navy md:px-6 md:py-6">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
          Budget snapshot
        </h3>
        <div className="mt-3 space-y-1.5 text-sm">
          <p>
            <span className="text-slate-500">You asked for</span>{" "}
            <span className="font-semibold text-brand-navy">
              ₹{String(budgetSummary?.target_budget_inr ?? "—")}
            </span>
          </p>
          <p>
            <span className="text-slate-500">Estimated total</span>{" "}
            <span className="font-semibold text-brand-leaf">
              ₹{String(budgetSummary?.optimized_total_cost_inr ?? "—")}
            </span>
          </p>
        </div>
        {!!judge?.issues?.length && (
          <ul className="mt-4 space-y-1 border-t border-slate-100 pt-3 text-xs text-slate-600">
            {judge.issues.slice(0, 3).map((issue) => (
              <li key={issue}>• {issue}</li>
            ))}
          </ul>
        )}
        {!!judge?.improved_suggestions?.length && (
          <ul className="mt-2 space-y-1 text-xs text-slate-500">
            {judge.improved_suggestions.slice(0, 3).map((suggestion) => (
              <li key={suggestion}>+ {suggestion}</li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
