"use client";

import { motion } from "framer-motion";

import type { DailyItineraryDay, PlanState, TripDayPhase } from "@/lib/types";

type Props = { plan: PlanState | null };

function dayIndexLabel(dayKey: string): string {
  const match = dayKey.match(/day_(\d+)/i);
  if (!match) return "—";
  const n = parseInt(match[1], 10);
  return String(n).padStart(2, "0");
}

function dayNumberFromKey(dayKey: string): string {
  const match = dayKey.match(/day_(\d+)/i);
  return match ? match[1] : "—";
}

function cardTitle(dayKey: string, day: DailyItineraryDay): string {
  const n = dayNumberFromKey(dayKey);
  if (day.headline) {
    return `Day ${n}: ${day.headline}`;
  }
  return dayKey.replace("_", " ");
}

function stayLine(day: DailyItineraryDay): string {
  return day.stay_summary?.trim() || day.stay?.trim() || "—";
}

function DaySections({ day }: { day: DailyItineraryDay }) {
  const phase = day.phase as TripDayPhase | undefined;
  const primary = (day.primary_transport_summary || "").trim();
  const local = (day.getting_around || "").trim();
  const legacyMobility =
    local ||
    (day as { transport?: string }).transport?.trim() ||
    "—";

  if (!phase) {
    return (
      <>
        <div>
          <dt className="text-[11px] font-semibold uppercase tracking-wide text-emerald-200/90">
            Getting around
          </dt>
          <dd className="whitespace-pre-line">{legacyMobility}</dd>
        </div>
        <div>
          <dt className="text-[11px] font-semibold uppercase tracking-wide text-emerald-200/90">
            Where you stay
          </dt>
          <dd className="whitespace-pre-line">{stayLine(day)}</dd>
        </div>
      </>
    );
  }

  if (phase === "reaching") {
    return (
      <>
        {primary ? (
          <div>
            <dt className="text-[11px] font-semibold uppercase tracking-wide text-emerald-200/90">
              Reaching destination
            </dt>
            <dd className="whitespace-pre-line">{primary}</dd>
          </div>
        ) : null}
        {local ? (
          <div>
            <dt className="text-[11px] font-semibold uppercase tracking-wide text-emerald-200/90">
              Getting around
            </dt>
            <dd className="whitespace-pre-line">{local}</dd>
          </div>
        ) : null}
        <div>
          <dt className="text-[11px] font-semibold uppercase tracking-wide text-emerald-200/90">
            Where you stay
          </dt>
          <dd className="whitespace-pre-line">{stayLine(day)}</dd>
        </div>
      </>
    );
  }

  if (phase === "return_home") {
    const localExtra =
      local && primary && local !== primary ? local : local && !primary ? local : "";
    return (
      <>
        {primary ? (
          <div>
            <dt className="text-[11px] font-semibold uppercase tracking-wide text-emerald-200/90">
              Return journey
            </dt>
            <dd className="whitespace-pre-line">{primary}</dd>
          </div>
        ) : null}
        {localExtra ? (
          <div>
            <dt className="text-[11px] font-semibold uppercase tracking-wide text-emerald-200/90">
              Before you go
            </dt>
            <dd className="whitespace-pre-line">{localExtra}</dd>
          </div>
        ) : null}
        <div>
          <dt className="text-[11px] font-semibold uppercase tracking-wide text-emerald-200/90">
            Where you stay
          </dt>
          <dd className="whitespace-pre-line">{stayLine(day)}</dd>
        </div>
      </>
    );
  }

  /* explore */
  const mobility =
    primary || local || "—";
  return (
    <>
      <div>
        <dt className="text-[11px] font-semibold uppercase tracking-wide text-emerald-200/90">
          Getting around
        </dt>
        <dd className="whitespace-pre-line">{mobility}</dd>
      </div>
      <div>
        <dt className="text-[11px] font-semibold uppercase tracking-wide text-emerald-200/90">
          Where you stay
        </dt>
        <dd className="whitespace-pre-line">{stayLine(day)}</dd>
      </div>
    </>
  );
}

export function ItineraryView({ plan }: Props) {
  const finalItinerary = plan?.final_itinerary;
  if (!finalItinerary) {
    return (
      <div className="rounded-2xl border border-dashed border-white/15 bg-white/5 p-10 text-center text-sm text-slate-400">
        Your itinerary will appear here when ready.
      </div>
    );
  }

  const days = Object.entries(finalItinerary.daily_plan ?? {});

  return (
    <div className="space-y-5">
      {days.map(([dayKey, day], index) => (
        <motion.article
          key={dayKey}
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.06 }}
          className="flex overflow-hidden rounded-2xl bg-white shadow-card ring-1 ring-black/5"
        >
          <div className="relative flex w-[4.5rem] shrink-0 flex-col items-center justify-center bg-slate-50 px-3 py-6 md:w-24">
            <span className="absolute -right-1 top-3 h-2 w-2 rounded-full bg-brand-navy" />
            <span className="absolute -right-1 bottom-3 h-2 w-2 rounded-full bg-brand-navy" />
            <span className="text-3xl font-bold tabular-nums text-brand-navy md:text-4xl">
              {dayIndexLabel(dayKey)}
            </span>
            <span className="mt-1 text-[10px] font-semibold uppercase tracking-wider text-slate-400">
              Day
            </span>
          </div>
          <div className="min-w-0 flex-1 bg-gradient-to-br from-brand-leaf to-emerald-700 px-5 py-5 text-white md:px-7 md:py-6">
            <h3 className="text-lg font-bold leading-snug text-white md:text-xl">
              {cardTitle(dayKey, day)}
            </h3>
            {day.headline ? null : day.theme ? (
              <p className="mt-2 text-sm font-medium text-emerald-50/95">{day.theme}</p>
            ) : null}
            <dl className="mt-4 space-y-3 text-sm text-emerald-50/90">
              <DaySections day={day} />
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-wide text-emerald-200/90">
                  Places & food
                </dt>
                <dd>
                  {(day.activities ?? []).join(", ")}
                  {(day.activities ?? []).length && (day.food ?? []).length ? " · " : ""}
                  {(day.food ?? []).join(", ")}
                </dd>
              </div>
            </dl>
          </div>
        </motion.article>
      ))}
    </div>
  );
}
