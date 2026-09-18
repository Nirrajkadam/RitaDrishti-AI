"use client";

import ReactECharts from "echarts-for-react";
import type { EChartsOption } from "echarts";
import { CHART_COLORS, CHART_PALETTE } from "@/lib/chart-theme";

const baseTextStyle = {
  fontFamily: "var(--font-manrope), system-ui, sans-serif",
  color: CHART_COLORS.ink,
  fontSize: 11,
};

export function withDefaults(option: EChartsOption): EChartsOption {
  return {
    color: CHART_PALETTE,
    textStyle: baseTextStyle,
    grid: { left: 8, right: 12, top: 28, bottom: 8, containLabel: true },
    tooltip: {
      backgroundColor: "#191C20",
      borderColor: "#262B31",
      borderWidth: 1,
      textStyle: { color: "#E9ECEF", fontSize: 12 },
      extraCssText: "border-radius:6px; box-shadow: 0 8px 24px rgba(0,0,0,0.4);",
    },
    ...option,
  };
}

export default function EChart({
  option,
  height = 260,
  className,
}: {
  option: EChartsOption;
  height?: number | string;
  className?: string;
}) {
  return (
    <ReactECharts
      option={withDefaults(option)}
      style={{ height, width: "100%" }}
      className={className}
      opts={{ renderer: "svg" }}
      theme="dark"
      notMerge
    />
  );
}
