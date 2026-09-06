import { Card } from "@/components/ui/card";

/** Every chart answers one written question (the title) and carries a
 * computed takeaway underneath — a chart without a conclusion is
 * decoration. Empty states teach the chart's shape rather than showing
 * a shrug. */
export function ChartCard({
  question,
  takeaway,
  isEmpty,
  emptyHint,
  children,
}: {
  question: string;
  takeaway: string;
  isEmpty?: boolean;
  emptyHint?: string;
  children: React.ReactNode;
}) {
  return (
    <Card className="p-4">
      <h3 className="text-sm font-semibold text-text mb-3">{question}</h3>
      <div className="min-h-[240px]" aria-hidden={isEmpty}>
        {children}
      </div>
      <p className="text-xs text-text-muted mt-2 leading-relaxed">
        {isEmpty ? emptyHint : takeaway}
      </p>
    </Card>
  );
}
