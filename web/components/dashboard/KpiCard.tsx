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
      <div className="text-3xl font-semibold tracking-tight tabular-nums" style={{ color: accent }}>
        {value}
      </div>
      <div className="text-xs text-text-faint mt-1">{label}</div>
    </Card>
  );
}
