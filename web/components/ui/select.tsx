import { forwardRef } from "react";
import { cn } from "@/lib/cn";

export const Select = forwardRef<HTMLSelectElement, React.SelectHTMLAttributes<HTMLSelectElement>>(
  ({ className, children, ...props }, ref) => (
    <select
      ref={ref}
      className={cn(
        "h-12 rounded-lg border border-border bg-surface-2 px-3 text-sm text-text",
        "focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent",
        "disabled:opacity-40",
        className
      )}
      {...props}
    >
      {children}
    </select>
  )
);
Select.displayName = "Select";
