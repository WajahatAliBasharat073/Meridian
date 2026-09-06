import { cva, type VariantProps } from "class-variance-authority";
import { forwardRef } from "react";
import { cn } from "@/lib/cn";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-colors " +
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 " +
    "focus-visible:ring-offset-bg disabled:opacity-40 disabled:pointer-events-none active:brightness-95",
  {
    variants: {
      variant: {
        primary: "bg-accent text-bg hover:brightness-110",
        secondary: "bg-surface-2 text-text hover:bg-surface-hover border border-border",
        ghost: "text-text-muted hover:text-text hover:bg-surface-2",
        danger: "bg-danger/15 text-danger hover:bg-danger/25",
      },
      // All four sizes share h-11 (44px) — the build prompt's own
      // minimum touch target (7). "sm" is more compact horizontally,
      // never shorter — a small footprint should never mean a smaller
      // tap zone.
      size: {
        sm: "h-11 px-3 text-xs",
        md: "h-11 px-4 text-sm",
        lg: "h-11 px-5 text-base",
        icon: "h-11 w-11",
      },
    },
    defaultVariants: { variant: "secondary", size: "md" },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => (
    <button ref={ref} className={cn(buttonVariants({ variant, size }), className)} {...props} />
  )
);
Button.displayName = "Button";
