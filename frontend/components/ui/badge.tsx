import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center gap-1.5 rounded-sm px-2 py-0.5 text-2xs font-medium tracking-wide",
  {
    variants: {
      variant: {
        neutral: "bg-graphite-700 text-ink-400 border border-line",
        signal: "bg-signal-faint text-signal border border-signal-dim/40",
        sight: "bg-sight-faint text-sight border border-sight/30",
        watch: "bg-risk-watchFaint text-risk-watch border border-risk-watch/30",
        elevated:
          "bg-risk-elevatedFaint text-risk-elevated border border-risk-elevated/30",
        critical:
          "bg-risk-criticalFaint text-risk-critical border border-risk-critical/30",
      },
    },
    defaultVariants: {
      variant: "neutral",
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {
  dot?: boolean;
}

function Badge({ className, variant, dot, children, ...props }: BadgeProps) {
  return (
    <span className={cn(badgeVariants({ variant }), className)} {...props}>
      {dot && (
        <span
          className={cn(
            "h-1.5 w-1.5 rounded-full",
            variant === "critical" && "bg-risk-critical animate-pulse-dot",
            variant === "elevated" && "bg-risk-elevated",
            variant === "watch" && "bg-risk-watch",
            variant === "sight" && "bg-sight",
            variant === "signal" && "bg-signal",
            variant === "neutral" && "bg-ink-600"
          )}
        />
      )}
      {children}
    </span>
  );
}

export { Badge, badgeVariants };
