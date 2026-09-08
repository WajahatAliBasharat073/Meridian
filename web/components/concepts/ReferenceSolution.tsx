"use client";

import { Code2 } from "lucide-react";

/** A real, working reference implementation — not the answer to copy
 * before attempting it, but the thing to check your own solution against
 * afterward. Collapsed by default for that reason: opening it is a
 * deliberate choice, not something that happens while scanning the card.
 *
 * Sourced from AIMLInterviews' actual `.py` files (MIT-licensed), read at
 * ingestion time — see `_read_reference_solution` in
 * api/scripts/ingest_curriculum.py. No syntax highlighting on purpose;
 * this is one code block on a page, not an editor. */
export function ReferenceSolution({ code }: { code: string }) {
  return (
    <details className="mb-4 group">
      <summary className="text-xs text-accent-strong cursor-pointer inline-flex items-center gap-1.5 list-none">
        <Code2 size={12} />
        Reference implementation
        <span className="text-text-faint font-normal">— try it yourself first</span>
      </summary>
      <pre className="mt-2 rounded-lg border border-border bg-surface-2/70 p-3 overflow-x-auto">
        <code className="text-[11px] font-mono text-text-muted leading-relaxed whitespace-pre">
          {code}
        </code>
      </pre>
    </details>
  );
}
