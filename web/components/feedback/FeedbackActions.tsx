"use client";

import { useState } from "react";

import { submitFeedback } from "@/lib/api";
import { FeedbackVote } from "@/lib/types";

type Props = {
  runId: string;
};

export function FeedbackActions({ runId }: Props) {
  const [status, setStatus] = useState<"idle" | "saving" | "saved" | "error">(
    "idle",
  );

  async function handleVote(vote: FeedbackVote) {
    if (!runId) return;
    setStatus("saving");
    try {
      await submitFeedback({ runId, vote });
      setStatus("saved");
    } catch {
      setStatus("error");
    }
  }

  if (!runId) return null;

  return (
    <div className="flex flex-col justify-center rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm md:min-h-[200px]">
      <p className="text-center text-xs font-bold uppercase tracking-widest text-slate-400">
        Was this helpful?
      </p>
      <div className="mt-5 flex justify-center gap-4">
        <button
          type="button"
          onClick={() => handleVote("up")}
          disabled={status === "saving"}
          className="flex h-14 w-14 items-center justify-center rounded-full border-2 border-white/20 bg-white/10 text-white transition hover:border-brand-orange hover:bg-brand-orange/20 disabled:opacity-50"
          aria-label="Up vote"
        >
          <svg className="h-6 w-6" viewBox="0 0 24 24" fill="none" aria-hidden>
            <path
              d="M12 4l8 8h-5v8H9v-8H4l8-8z"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinejoin="round"
            />
          </svg>
        </button>
        <button
          type="button"
          onClick={() => handleVote("down")}
          disabled={status === "saving"}
          className="flex h-14 w-14 items-center justify-center rounded-full border-2 border-white/20 bg-white/10 text-white transition hover:border-white/40 hover:bg-white/15 disabled:opacity-50"
          aria-label="Down vote"
        >
          <svg className="h-6 w-6" viewBox="0 0 24 24" fill="none" aria-hidden>
            <path
              d="M12 20l-8-8h5V4h6v8h5l-8 8z"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </div>
      {status === "saved" && (
        <p className="mt-4 text-center text-xs font-medium text-emerald-300/90">
          Thanks — we&apos;ve noted your feedback.
        </p>
      )}
      {status === "error" && (
        <p className="mt-4 text-center text-xs text-red-300/90">
          Could not save feedback. Try again.
        </p>
      )}
    </div>
  );
}
