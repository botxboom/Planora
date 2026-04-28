"use client";

import { useMemo, useRef, useState } from "react";

import { streamPlan } from "@/lib/api";
import { PlanState, StreamEnvelope } from "@/lib/types";

export function usePlanStream() {
  const [events, setEvents] = useState<StreamEnvelope[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [finalResult, setFinalResult] = useState<PlanState | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  async function startStream(query: string, userId?: string) {
    setEvents([]);
    setError(null);
    setFinalResult(null);
    setIsStreaming(true);

    const abortController = new AbortController();
    abortRef.current = abortController;

    try {
      await streamPlan(
        { query, user_id: userId },
        (event) => {
          setEvents((previous) => [...previous, event]);
          if (event.event === "final_result") {
            setFinalResult((event.data.result as PlanState) ?? null);
          }
          if (event.event === "error") {
            setError(String(event.data.message ?? "Stream error."));
          }
        },
        abortController.signal,
      );
    } catch (streamError) {
      if (!abortController.signal.aborted) {
        setError((streamError as Error).message);
      }
    } finally {
      setIsStreaming(false);
    }
  }

  function stopStream() {
    abortRef.current?.abort();
    setIsStreaming(false);
  }

  const runId = useMemo(
    () => finalResult?.metadata?.run_id ?? "",
    [finalResult],
  );

  return {
    startStream,
    stopStream,
    events,
    isStreaming,
    error,
    finalResult,
    runId,
  };
}
