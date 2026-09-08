import { Info } from "lucide-react";

/** Shown wherever an analytic has no real data behind it yet.
 *
 * Deliberately says what's missing and what would fill it, instead of
 * rendering placeholder numbers. Invented figures here would be worse than
 * an empty panel: they'd be indistinguishable from real history and would
 * silently corrupt every decision made by reading this page. */
export function NoDataYet({ what, fills }: { what: string; fills: string }) {
  return (
    <div className="rounded-xl border border-dashed border-border bg-surface-2/30 p-5 text-center">
      <Info size={16} className="mx-auto text-text-faint mb-2" />
      <p className="text-sm text-text-muted">No {what} recorded yet.</p>
      <p className="text-xs text-text-faint mt-1 max-w-md mx-auto leading-relaxed">{fills}</p>
    </div>
  );
}
