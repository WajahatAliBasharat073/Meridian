import { Card } from "@/components/ui/card";

export function KpiCard({
  value,
  label,
  accent,
}: {
  value: string;
  label: string;
  accent?: string;
}) {
  return (
    <Card className="p-4">
      <div className="text-xs text-text-faint">{label}</div>
      <div className="text-2xl sm:text-3xl font-semibold tracking-tight tabular-nums mt-2" style={{ color: accent }}>
        {value}
      </div>
    </Card>
  );
}
