import type { LucideIcon } from "lucide-react";
import { EmptyState } from "@/components/ui/empty-state";

export function ComingSoon({
  icon,
  title,
  description,
}: {
  icon: LucideIcon;
  title: string;
  description: string;
}) {
  return (
    <EmptyState
      icon={icon}
      title={`${title} is not available yet`}
      description={description}
    />
  );
}
