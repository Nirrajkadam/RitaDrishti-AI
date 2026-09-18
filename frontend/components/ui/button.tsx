import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-sm text-[13px] font-medium transition-colors disabled:pointer-events-none disabled:opacity-40 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-signal",
  {
    variants: {
      variant: {
        default: "bg-signal text-white hover:bg-signal-dim",
        outline:
          "border border-line bg-transparent text-ink-100 hover:bg-graphite-700",
        ghost: "text-ink-400 hover:text-ink-100 hover:bg-graphite-700",
        subtle: "bg-graphite-700 text-ink-100 hover:bg-graphite-600",
        destructive: "bg-risk-critical text-white hover:opacity-90",
      },
      size: {
        default: "h-8 px-3",
        sm: "h-7 px-2.5 text-2xs",
        lg: "h-9 px-4",
        icon: "h-8 w-8",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

export { Button, buttonVariants };
