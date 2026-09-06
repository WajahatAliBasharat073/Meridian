import type { LucideIcon } from "lucide-react";
import { Card } from "@/components/ui/card";

export function EmptyState({
  icon: Icon,
  title,
  description,
  action,
}: {
  icon: LucideIcon;
  title: string;
  description: string;
  action?: React.ReactNode;
}) {
  return (
    <Card className="p-10 sm:p-12 text-center flex flex-col items-center">
      <div className="h-12 w-12 rounded-xl bg-surface-2 border border-border flex items-center justify-center mb-4">
        <Icon size={22} className="text-text-faint" aria-hidden />
      </div>
      <h3 className="text-base font-semibold text-text">{title}</h3>
      <p className="text-sm text-text-muted mt-1.5 max-w-sm leading-relaxed">{description}</p>
      {action && <div className="mt-5">{action}</div>}
    </Card>
  );
}
