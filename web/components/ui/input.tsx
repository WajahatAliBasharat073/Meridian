import { forwardRef } from "react";
import { cn } from "@/lib/cn";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  /** Rendered inside the field, left-aligned — e.g. a lucide-react icon. */
  icon?: React.ReactNode;
  /** Rendered inside the field, right-aligned — e.g. a show/hide toggle. */
  trailing?: React.ReactNode;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, icon, trailing, ...props }, ref) => (
    <div className="relative">
      {icon && (
        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-text-faint pointer-events-none">
          {icon}
        </span>
      )}
      <input
        ref={ref}
        className={cn(
          "w-full h-12 rounded-lg border border-border bg-surface-2 text-sm text-text placeholder:text-text-faint",
          "focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent transition-shadow",
          icon ? "pl-10" : "pl-3",
          trailing ? "pr-11" : "pr-3",
          className
        )}
        {...props}
      />
      {trailing && (
        <span className="absolute right-2 top-1/2 -translate-y-1/2">{trailing}</span>
      )}
    </div>
  )
);
Input.displayName = "Input";
