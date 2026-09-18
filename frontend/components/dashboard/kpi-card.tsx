import { ArrowDownRight, ArrowUpRight, type LucideIcon } from "lucide-react";
import { cn, formatDelta } from "@/lib/utils";

export function KpiCard({
  label,
  value,
  unit,
  delta,
  deltaGood = true,
  icon: Icon,
  sparklineDesc,
}: {
  label: string;
  value: string;
  unit?: string;
  delta?: number;
  deltaGood?: boolean;
  icon?: LucideIcon;
  sparklineDesc?: string;
}) {
  const positive = (delta ?? 0) >= 0;
  const isGood = deltaGood ? positive : !positive;

  return (
    <div className="panel px-4 py-3.5 flex flex-col gap-2.5">
      <div className="flex items-center justify-between">
        <span className="text-2xs font-medium text-ink-600 tracking-wide">
          {label}
        </span>
        {Icon && <Icon className="h-3.5 w-3.5 text-ink-600" strokeWidth={1.75} />}
      </div>
      <div className="flex items-baseline gap-1.5">
        <span className="text-2xl font-semibold tracking-tight text-ink-100 tabular">
          {value}
        </span>
        {unit && <span className="text-xs text-ink-600">{unit}</span>}
      </div>
      <div className="flex items-center gap-1.5">
        {delta !== undefined && (
          <span
            className={cn(
              "inline-flex items-center gap-0.5 text-2xs font-medium tabular",
              isGood ? "text-sight" : "text-risk-critical"
            )}
          >
            {positive ? (
              <ArrowUpRight className="h-3 w-3" />
            ) : (
              <ArrowDownRight className="h-3 w-3" />
            )}
            {formatDelta(delta)}
          </span>
        )}
        {sparklineDesc && (
          <span className="text-2xs text-ink-600">{sparklineDesc}</span>
        )}
      </div>
    </div>
  );
}
