"use client";

type Props = {
  query: string;
  onQueryChange: (value: string) => void;
  onSubmit: () => void;
  disabled?: boolean;
};

/**
 * Floating white search-style card — SnapTrips-inspired: large radius, shadow, primary CTA with accent dot.
 */
export function ChatComposer({ query, onQueryChange, onSubmit, disabled }: Props) {
  return (
    <div className="overflow-hidden rounded-[1.75rem] bg-white shadow-float ring-1 ring-slate-200/80">
      <label htmlFor="trip-prompt" className="sr-only">
        Describe your trip
      </label>
      <textarea
        id="trip-prompt"
        value={query}
        onChange={(event) => onQueryChange(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            if (!disabled && query.trim().length >= 3) onSubmit();
          }
        }}
        className="min-h-[120px] w-full resize-none border-0 bg-transparent px-6 py-5 text-base leading-relaxed text-brand-navy placeholder:text-slate-400 focus:outline-none focus:ring-0 md:min-h-[140px] md:text-lg"
        placeholder="Tell us where you’re going, how long you’ll stay, and what matters most…"
      />
      <div className="flex items-center justify-end gap-3 border-t border-slate-100 px-4 py-3 md:px-5">
        <button
          type="button"
          onClick={onSubmit}
          disabled={disabled || query.trim().length < 3}
          className="group inline-flex items-center gap-3 rounded-full bg-brand-navy px-6 py-3 text-sm font-semibold text-white shadow-md transition hover:bg-brand-navyDeep disabled:cursor-not-allowed disabled:opacity-45"
        >
          Plan my trip
          <span className="flex h-9 w-9 items-center justify-center rounded-full bg-brand-orange text-white transition group-hover:bg-brand-orangeDeep">
            <svg className="h-4 w-4 -translate-x-px" viewBox="0 0 24 24" fill="none" aria-hidden>
              <path
                d="M5 12h14M13 6l6 6-6 6"
                stroke="currentColor"
                strokeWidth="2.2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </span>
        </button>
      </div>
    </div>
  );
}
