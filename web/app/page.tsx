"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useState } from "react";

import { BrushUnderline } from "@/components/brand/BrushUnderline";
import { PlanoraMark } from "@/components/brand/PlanoraMark";
import { ChatComposer } from "@/components/chat/ChatComposer";
import { FeedbackActions } from "@/components/feedback/FeedbackActions";
import { ItineraryView } from "@/components/itinerary/ItineraryView";
import { JudgeScoreCard } from "@/components/judge/JudgeScoreCard";
import { PlanningStatus } from "@/components/hero/PlanningStatus";
import { TravelAtmosphere } from "@/components/hero/TravelAtmosphere";
import { usePlanStream } from "@/hooks/usePlanStream";
import { PlanState } from "@/lib/types";

const DEFAULT_QUERY =
  "Plan a 4-day trip to Goa from Bangalore under ₹25,000 with good food and minimal travel time";

export default function HomePage() {
  const [query, setQuery] = useState(DEFAULT_QUERY);
  const { startStream, events, isStreaming, error, finalResult, runId } =
    usePlanStream();

  const hasResult = Boolean(finalResult?.final_itinerary);

  return (
    <main className="min-h-screen">
      {/* —— Hero (illustrated, light) —— */}
      <section className="relative min-h-[88vh] overflow-hidden pb-16 pt-6 md:min-h-[90vh] md:pb-24 md:pt-8">
        <TravelAtmosphere />

        <header className="relative z-20 mx-auto flex max-w-6xl items-center justify-between px-4 md:px-8">
          <div className="flex items-center gap-3">
            <PlanoraMark className="h-9 w-9 shrink-0" />
            <span className="text-xl font-bold tracking-tight text-brand-navy md:text-2xl">
              Planora
            </span>
          </div>
        </header>

        <div className="relative z-20 mx-auto mt-10 max-w-4xl px-4 md:mt-16 md:px-8">
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.55 }}
          >
            <h1 className="text-balance text-3xl font-bold leading-tight tracking-tight text-brand-navy md:text-5xl md:leading-[1.15]">
              Inspiring{" "}
              <BrushUnderline>explorations</BrushUnderline>
              <br className="hidden sm:block" />
              <span className="sm:ml-1">and endless possibilities</span>
            </h1>
            <p className="mt-5 max-w-2xl text-base leading-relaxed text-slate-600 md:text-lg">
              Discover quick, thoughtful trip plans tailored to your budget and
              style. Describe your journey — we&apos;ll craft the rest.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.55, delay: 0.1 }}
            className="mt-10 space-y-5 md:mt-12"
          >
            <ChatComposer
              query={query}
              onQueryChange={setQuery}
              onSubmit={() => void startStream(query)}
              disabled={isStreaming}
            />
            <PlanningStatus
              events={events}
              isStreaming={isStreaming}
              variant="light"
            />
            {error && (
              <p
                className="text-center text-sm font-medium text-red-600"
                role="alert"
              >
                {error}
              </p>
            )}
          </motion.div>
        </div>
      </section>

      {/* —— Results (deep navy, SnapTrips-style CTA section) —— */}
      <AnimatePresence>
        {hasResult && finalResult && (
          <motion.section
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.4 }}
            className="relative overflow-hidden bg-brand-navy pb-20 pt-16 text-white md:pb-28 md:pt-20"
          >
            {/* Decorative foliage */}
            <svg
              className="pointer-events-none absolute right-0 top-0 h-[70%] w-[45%] max-w-lg text-brand-leaf/25"
              viewBox="0 0 200 400"
              aria-hidden
            >
              <path
                d="M180,400 Q140,200 160,40 L200,0 L200,400 Z"
                fill="currentColor"
              />
              <path
                d="M120,400 Q100,280 130,140"
                stroke="currentColor"
                strokeWidth="6"
                fill="none"
                strokeLinecap="round"
              />
            </svg>
            <motion.svg
              className="pointer-events-none absolute bottom-10 left-[5%] w-32 text-amber-400/20 md:left-[8%]"
              viewBox="0 0 120 24"
              aria-hidden
              animate={{ opacity: [0.5, 0.85, 0.5] }}
              transition={{ duration: 6, repeat: Infinity }}
            >
              <path
                d="M0,16 Q40,4 80,14 T120,12"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
              />
            </motion.svg>

            <div className="relative z-10 mx-auto max-w-4xl px-4 md:px-8">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.45 }}
                className="mb-12 text-center md:text-left"
              >
                <h2 className="text-balance text-2xl font-bold leading-tight md:text-4xl">
                  Your <BrushUnderline>curated</BrushUnderline> itinerary
                  <br />
                  <span className="text-slate-100">is ready</span>
                </h2>
                <p className="mt-4 max-w-xl text-sm leading-relaxed text-slate-300 md:text-base">
                  From transport and stays to places and dining — everything in
                  one place, tuned to what you asked for.
                </p>
              </motion.div>

              <div className="space-y-8">
                <ItineraryView plan={finalResult as PlanState} />
                <div className="grid gap-6 md:grid-cols-2">
                  <JudgeScoreCard plan={finalResult as PlanState} />
                  {runId ? <FeedbackActions runId={runId} /> : null}
                </div>
              </div>
            </div>
          </motion.section>
        )}
      </AnimatePresence>
    </main>
  );
}
