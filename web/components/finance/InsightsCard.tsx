import { Lightbulb } from "lucide-react";
import { Card } from "@/components/ui/card";

/** The dashboard's actual decisions, one sentence each -- computed by
 * app/engines/finance.py's build_insights, never templated filler. No
 * card at all when there's nothing worth saying, rather than an empty
 * "no insights yet" placeholder competing for attention. */
export function InsightsCard({ insights }: { insights: string[] }) {
  if (insights.length === 0) return null;

  return (
    <Card className="p-4">
      <h3 className="text-sm font-semibold text-text mb-3 flex items-center gap-2">
        <Lightbulb size={15} className="text-accent" /> What this means
      </h3>
      <ul className="space-y-2">
        {insights.map((line) => (
          <li key={line} className="text-sm text-text-muted leading-relaxed pl-3 border-l-2 border-accent/40">
            {line}
          </li>
        ))}
      </ul>
    </Card>
  );
}
