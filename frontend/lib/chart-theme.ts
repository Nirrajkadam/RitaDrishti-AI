/**
 * Chart color tokens, kept in a plain module (no "use client") so server
 * components can import them directly without crossing the RSC boundary.
 * The ECharts wrapper (components/charts/echart.tsx) also reads from here.
 */
export const CHART_COLORS = {
  signal: "#6E6BFF",
  sight: "#35C7B5",
  watch: "#E8A33D",
  elevated: "#E2793D",
  critical: "#E5484D",
  ink: "#939BA8",
  line: "#22262B",
} as const;

export const CHART_PALETTE = [
  CHART_COLORS.signal,
  CHART_COLORS.sight,
  CHART_COLORS.watch,
  CHART_COLORS.elevated,
  "#4B49B0",
  "#5B6270",
];
