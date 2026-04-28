/** Small logo mark — sun / compass motif in brand orange. */
export function PlanoraMark({ className = "h-8 w-8" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 32 32" fill="none" aria-hidden>
      <circle cx="16" cy="16" r="14" className="fill-brand-orange" />
      <circle cx="16" cy="16" r="5" className="fill-white" />
      <path
        d="M16 2v4M16 26v4M2 16h4M26 16h4M5.5 5.5l2.8 2.8M23.7 23.7l2.8 2.8M5.5 26.5l2.8-2.8M23.7 8.3l2.8-2.8"
        stroke="white"
        strokeWidth="1.5"
        strokeLinecap="round"
        opacity="0.9"
      />
    </svg>
  );
}
