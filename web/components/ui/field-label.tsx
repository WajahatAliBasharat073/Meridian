import { cn } from "@/lib/cn";

interface FieldLabelProps extends React.LabelHTMLAttributes<HTMLLabelElement> {
  hint?: string;
}

export function FieldLabel({ className, hint, children, ...props }: FieldLabelProps) {
  return (
    <div className="flex items-baseline justify-between mb-1.5">
      <label className={cn("text-xs font-medium text-text-faint", className)} {...props}>
        {children}
      </label>
      {hint && <span className="text-[11px] text-text-faint">{hint}</span>}
    </div>
  );
}
