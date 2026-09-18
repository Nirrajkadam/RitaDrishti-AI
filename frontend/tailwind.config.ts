import type { Config } from "tailwindcss";

/**
 * RitaDrishti AI — design tokens
 *
 * Palette (named):
 *   void       #0A0B0D  page background, deepest layer
 *   graphite-9 #121417  sidebar / topbar surface
 *   graphite-8 #191C20  card surface
 *   graphite-7 #22262B  raised / hover surface
 *   line       #262B31  hairline borders
 *   ink-100    #E9ECEF  primary text
 *   ink-400    #939BA8  secondary text
 *   ink-600    #5B6270  disabled / tertiary text
 *   signal     #6E6BFF  primary intelligence accent (AI, links, focus)
 *   sight      #35C7B5  trust / verified / positive
 *   amber      #E8A33D  risk — watch
 *   ember      #E2793D  risk — elevated
 *   crimson    #E5484D  risk — critical
 *
 * Type: Manrope (UI + headings), IBM Plex Mono (metrics, ids, timestamps only)
 */
const config: Config = {
  darkMode: ["class"],
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        void: "#0A0B0D",
        graphite: {
          900: "#121417",
          800: "#191C20",
          700: "#22262B",
          600: "#2B3036",
        },
        line: "#262B31",
        ink: {
          100: "#E9ECEF",
          400: "#939BA8",
          600: "#5B6270",
        },
        signal: {
          DEFAULT: "#6E6BFF",
          dim: "#4B49B0",
          faint: "#211F55",
        },
        sight: {
          DEFAULT: "#35C7B5",
          faint: "#12312D",
        },
        risk: {
          watch: "#E8A33D",
          elevated: "#E2793D",
          critical: "#E5484D",
          watchFaint: "#332811",
          elevatedFaint: "#331F11",
          criticalFaint: "#331515",
        },
      },
      fontFamily: {
        sans: ["var(--font-manrope)", "system-ui", "sans-serif"],
        mono: ["var(--font-plex-mono)", "ui-monospace", "monospace"],
      },
      fontSize: {
        "2xs": ["0.6875rem", { lineHeight: "1rem", letterSpacing: "0.01em" }],
      },
      borderRadius: {
        sm: "3px",
        DEFAULT: "5px",
        md: "6px",
        lg: "8px",
      },
      boxShadow: {
        panel: "0 1px 0 0 rgba(255,255,255,0.02) inset",
      },
      backgroundImage: {
        "grid-fade":
          "linear-gradient(to bottom, rgba(110,107,255,0.08), transparent 60%)",
      },
      keyframes: {
        "pulse-dot": {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.35" },
        },
        "sweep": {
          "0%": { transform: "translateX(-100%)" },
          "100%": { transform: "translateX(100%)" },
        },
      },
      animation: {
        "pulse-dot": "pulse-dot 2s ease-in-out infinite",
        sweep: "sweep 2.4s ease-in-out infinite",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
