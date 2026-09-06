import { cn } from "@/lib/cn";

export function PageHeader({
  eyebrow,
  title,
  description,
  action,
  className,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  action?: React.ReactNode;
  className?: string;
}) {
  return (
    <header className={cn("flex items-start justify-between gap-4 mb-6", className)}>
      <div className="min-w-0">
        {eyebrow && (
          <p className="text-xs font-medium uppercase tracking-wide text-text-faint mb-1">
            {eyebrow}
          </p>
        )}
        <h1 className="text-2xl font-semibold tracking-tight text-text text-balance">{title}</h1>
        {description && (
          <p className="text-sm text-text-muted mt-1 leading-relaxed max-w-2xl">{description}</p>
        )}
      </div>
      {action && <div className="shrink-0">{action}</div>}
    </header>
  );
}
