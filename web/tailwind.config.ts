import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./hooks/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          navy: "#0c1929",
          navyDeep: "#070f1a",
          sky: "#e0f2fe",
          teal: "#0f766e",
          leaf: "#15803d",
          leafLight: "#4ade80",
          orange: "#f97316",
          orangeDeep: "#ea580c",
          cream: "#f8fafc",
        },
        ocean: {
          50: "#f0f9ff",
          100: "#e0f2fe",
          500: "#0ea5e9",
          700: "#0369a1",
          900: "#082f49",
        },
      },
      fontFamily: {
        sans: ["var(--font-plus-jakarta)", "system-ui", "sans-serif"],
      },
      boxShadow: {
        glow: "0 20px 80px rgba(14,165,233,0.18)",
        hero: "inset 0 1px 0 rgba(255,255,255,0.06), 0 24px 80px rgba(0,0,0,0.45)",
        card: "0 25px 50px -12px rgba(15, 23, 42, 0.15)",
        float: "0 20px 60px rgba(12, 25, 41, 0.12)",
      },
    },
  },
  plugins: [],
};

export default config;
