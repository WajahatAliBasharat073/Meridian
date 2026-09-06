import { cn } from "@/lib/cn";

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  color?: string; // CSS color value — always paired with visible text (never colour alone)
}

export function Badge({ className, color, style, children, ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium leading-none",
        className
      )}
      style={{
        backgroundColor: color ? `color-mix(in srgb, ${color} 18%, transparent)` : undefined,
        color: color ?? undefined,
        ...style,
      }}
      {...props}
    >
      {children}
    </span>
  );
}
