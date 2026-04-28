"use client";

type Props = {
  children: React.ReactNode;
};

/** Hand-drawn style accent underline (SnapTrips-inspired). */
export function BrushUnderline({ children }: Props) {
  return (
    <span className="relative inline-block px-0.5">
      {children}
      <svg
        className="pointer-events-none absolute -bottom-1 left-0 h-3 w-full min-w-[3rem] text-brand-orange"
        viewBox="0 0 120 14"
        preserveAspectRatio="none"
        aria-hidden
      >
        <path
          d="M2 10 C28 4, 52 12, 78 8 C95 6, 108 4, 118 9"
          fill="none"
          stroke="currentColor"
          strokeWidth="5"
          strokeLinecap="round"
          opacity="0.92"
        />
      </svg>
    </span>
  );
}
