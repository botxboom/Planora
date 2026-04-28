"use client";

import { motion } from "framer-motion";

/**
 * Hero scenery: soft sky, layered hills, water, foliage — SnapTrips-style flat illustration with subtle motion.
 */
export function TravelAtmosphere() {
  return (
    <div
      className="pointer-events-none absolute inset-0 overflow-hidden"
      aria-hidden
    >
      {/* Sky */}
      <div className="absolute inset-0 bg-gradient-to-b from-sky-100 via-cyan-50/90 to-emerald-50/80" />

      {/* Distant mountains */}
      <svg
        className="absolute bottom-[32%] left-0 right-0 h-[38%] w-full text-teal-700/25"
        viewBox="0 0 1200 200"
        preserveAspectRatio="none"
      >
        <path d="M0,200 L0,120 L200,80 L400,100 L600,60 L800,90 L1000,70 L1200,100 L1200,200 Z" fill="currentColor" />
      </svg>
      <svg
        className="absolute bottom-[28%] left-0 right-0 h-[32%] w-full text-emerald-800/30"
        viewBox="0 0 1200 180"
        preserveAspectRatio="none"
      >
        <path d="M0,180 L0,100 L300,130 L500,70 L700,100 L900,85 L1200,110 L1200,180 Z" fill="currentColor" />
      </svg>

      {/* Water */}
      <motion.div
        className="absolute bottom-0 left-0 right-0 h-[30%] bg-gradient-to-b from-sky-300/40 to-sky-500/50"
        animate={{ opacity: [0.85, 1, 0.85] }}
        transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
      />

      {/* Sun */}
      <div className="absolute right-[12%] top-[10%] h-24 w-24 rounded-full bg-amber-100/90 blur-sm md:h-28 md:w-28" />
      <div className="absolute right-[14%] top-[12%] h-16 w-16 rounded-full bg-amber-50 md:h-20 md:w-20" />

      {/* Clouds */}
      <motion.svg
        className="absolute left-[8%] top-[14%] h-12 w-40 text-white/90 md:h-14 md:w-48"
        viewBox="0 0 160 48"
        animate={{ x: [0, 12, 0] }}
        transition={{ duration: 22, repeat: Infinity, ease: "easeInOut" }}
      >
        <ellipse cx="50" cy="28" rx="28" ry="14" fill="currentColor" />
        <ellipse cx="78" cy="26" rx="34" ry="18" fill="currentColor" />
        <ellipse cx="110" cy="30" rx="22" ry="12" fill="currentColor" />
      </motion.svg>
      <motion.svg
        className="absolute left-[40%] top-[8%] h-10 w-32 text-white/70"
        viewBox="0 0 140 40"
        animate={{ x: [0, -10, 0] }}
        transition={{ duration: 18, repeat: Infinity, ease: "easeInOut", delay: 2 }}
      >
        <ellipse cx="40" cy="24" rx="22" ry="11" fill="currentColor" />
        <ellipse cx="68" cy="22" rx="28" ry="14" fill="currentColor" />
      </motion.svg>

      {/* Birds */}
      <motion.svg
        className="absolute left-[25%] top-[18%] h-6 w-16 text-brand-navy/25"
        viewBox="0 0 80 24"
        animate={{ x: [0, 30, 0], y: [0, -4, 0] }}
        transition={{ duration: 24, repeat: Infinity, ease: "easeInOut" }}
      >
        <path
          d="M4,14 Q12,10 20,14 M28,12 Q36,8 44,12 M52,14 Q60,10 68,14"
          stroke="currentColor"
          strokeWidth="1.5"
          fill="none"
          strokeLinecap="round"
        />
      </motion.svg>

      {/* Right foliage */}
      <motion.svg
        className="absolute -right-4 bottom-[18%] h-[55%] w-[42%] max-w-md text-brand-leaf/35 md:right-0"
        viewBox="0 0 200 320"
        initial={{ opacity: 0.9 }}
        animate={{ rotate: [0, 1.2, 0], y: [0, -3, 0] }}
        transition={{ duration: 14, repeat: Infinity, ease: "easeInOut" }}
      >
        <path
          d="M120,320 Q100,200 140,80 Q160,40 180,20 L200,0 L200,320 Z"
          fill="currentColor"
          opacity="0.5"
        />
        <path
          d="M80,320 Q60,220 100,120 Q130,60 160,40"
          stroke="currentColor"
          strokeWidth="8"
          fill="none"
          strokeLinecap="round"
          opacity="0.6"
        />
        <ellipse cx="150" cy="100" rx="14" ry="36" fill="#f472b6" opacity="0.15" transform="rotate(-12 150 100)" />
        <ellipse cx="130" cy="160" rx="12" ry="28" fill="#fbbf24" opacity="0.2" transform="rotate(8 130 160)" />
      </motion.svg>

      {/* Decorative wave line (yellow accent) */}
      <svg
        className="absolute bottom-[26%] left-0 right-0 h-16 w-full text-amber-400/40"
        viewBox="0 0 1200 40"
        preserveAspectRatio="none"
      >
        <path
          d="M0,28 Q200,8 400,24 T800,20 T1200,26"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
        />
      </svg>

      {/* Island / cabin hint — small flat shape */}
      <svg
        className="absolute bottom-[22%] left-[42%] h-20 w-28 text-teal-800/20 md:left-[45%]"
        viewBox="0 0 100 80"
      >
        <path d="M10,70 L50,30 L90,70 Z" fill="currentColor" />
        <rect x="38" y="38" width="24" height="22" fill="white" opacity="0.35" rx="1" />
      </svg>
    </div>
  );
}
