"use client";

import { AnimatePresence, motion } from "framer-motion";

import { getFriendlyStatus } from "@/lib/planStatus";
import { StreamEnvelope } from "@/lib/types";

type Props = {
  events: StreamEnvelope[];
  isStreaming: boolean;
  variant?: "light" | "dark";
};

export function PlanningStatus({
  events,
  isStreaming,
  variant = "light",
}: Props) {
  const lastEvent = events.length > 0 ? events[events.length - 1] : null;
  const message = getFriendlyStatus(lastEvent, isStreaming);

  if (!message) {
    return null;
  }

  const textClass =
    variant === "dark" ? "text-slate-300" : "text-slate-600";
  const spinnerRing =
    variant === "dark"
      ? "border-white/25 border-t-brand-orange"
      : "border-slate-300/80 border-t-brand-teal";

  return (
    <div
      role="status"
      aria-live="polite"
      className={`flex min-h-[1.5rem] items-center justify-center gap-2.5 text-sm ${textClass}`}
    >
      <span
        className={`inline-block size-3.5 shrink-0 animate-spin rounded-full border-2 ${spinnerRing}`}
        aria-hidden
      />
      <AnimatePresence mode="wait">
        <motion.p
          key={message}
          initial={{ opacity: 0, y: 4 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -4 }}
          transition={{ duration: 0.25 }}
          className="text-center font-medium"
        >
          {message}
        </motion.p>
      </AnimatePresence>
    </div>
  );
}
