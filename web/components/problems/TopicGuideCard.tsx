"use client";

import { useState } from "react";
import { AlertTriangle, BookOpen, ChevronDown, Key, Layers, RotateCcw } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/cn";
import type { TopicGuideOut } from "@/lib/types";

/** "Understand the structure, then solve its problems" — deliberately
 * rendered *above* the problem list and open by default until the topic has
 * real progress, because going straight at the problems without knowing the
 * structure is the exact failure mode this is here to prevent. */
export function TopicGuideCard({
  guide,
  defaultOpen = false,
}: {
  guide: TopicGuideOut;
  defaultOpen?: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <Card
      className={cn(
        "p-0 overflow-hidden",
        guide.needs_revision ? "border-status-partial/50" : "border-accent/30"
      )}
    >
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        className="w-full text-left p-4 flex items-start gap-3 hover:bg-surface-2/40 transition-colors"
      >
        <span
          className="h-9 w-9 shrink-0 rounded-lg flex items-center justify-center"
          style={{
            backgroundColor: guide.needs_revision
              ? "color-mix(in srgb, var(--status-partial) 15%, transparent)"
              : "color-mix(in srgb, var(--accent) 15%, transparent)",
            color: guide.needs_revision ? "var(--status-partial)" : "var(--accent-strong)",
          }}
          aria-hidden
        >
          {guide.needs_revision ? <RotateCcw size={17} /> : <BookOpen size={17} />}
        </span>

        <span className="min-w-0 flex-1">
          <span className="flex items-center gap-2 flex-wrap">
            <span className="text-sm font-semibold text-text">
              {guide.needs_revision
                ? `Revise ${guide.display_name.replace(" (revision)", "")}`
                : `Learn ${guide.display_name} first`}
            </span>
            {guide.needs_revision && (
              <Badge color="var(--status-partial)">Needs revision</Badge>
            )}
          </span>
          <span className="block text-xs text-text-muted mt-1 leading-relaxed">
            {guide.one_liner}
          </span>
        </span>

        <ChevronDown
          size={16}
          className={cn("shrink-0 mt-1 text-text-faint transition-transform", open && "rotate-180")}
        />
      </button>

      {open && (
        <div className="px-4 pb-4 pt-1 space-y-4 border-t border-border">
          <p className="text-xs text-text-muted leading-relaxed">{guide.learn_first}</p>

          {guide.types.length > 0 && (
            <section>
              <h4 className="text-[10px] uppercase tracking-wide text-text-faint mb-2 flex items-center gap-1.5">
                <Layers size={11} /> Types & variants
              </h4>
              <ul className="grid sm:grid-cols-2 gap-1.5">
                {guide.types.map((t) => (
                  <li
                    key={t.name}
                    className="rounded-lg border border-border bg-surface-2/40 px-2.5 py-2"
                  >
                    <span className="text-xs font-medium text-text">{t.name}</span>
                    <span className="block text-[11px] text-text-faint mt-0.5 leading-relaxed">
                      {t.note}
                    </span>
                  </li>
                ))}
              </ul>
            </section>
          )}

          {guide.operations.length > 0 && (
            <section>
              <h4 className="text-[10px] uppercase tracking-wide text-text-faint mb-2">
                Core operations & cost
              </h4>
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <tbody className="divide-y divide-border">
                    {guide.operations.map((o) => (
                      <tr key={o.op}>
                        <td className="py-1.5 pr-3 text-text align-top whitespace-nowrap">
                          {o.op}
                        </td>
                        <td className="py-1.5 pr-3 align-top whitespace-nowrap font-mono tabular-nums text-accent-strong">
                          {o.complexity}
                        </td>
                        <td className="py-1.5 text-text-faint align-top leading-relaxed">
                          {o.note}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}

          <div className="grid sm:grid-cols-2 gap-4">
            {guide.must_know.length > 0 && (
              <section>
                <h4 className="text-[10px] uppercase tracking-wide text-text-faint mb-2 flex items-center gap-1.5">
                  <Key size={11} /> Techniques that unlock this topic
                </h4>
                <ul className="space-y-1">
                  {guide.must_know.map((m) => (
                    <li key={m} className="text-[11px] text-text-muted leading-relaxed flex gap-1.5">
                      <span className="text-accent-strong shrink-0" aria-hidden>
                        ·
                      </span>
                      {m}
                    </li>
                  ))}
                </ul>
              </section>
            )}

            {guide.pitfalls.length > 0 && (
              <section>
                <h4 className="text-[10px] uppercase tracking-wide text-text-faint mb-2 flex items-center gap-1.5">
                  <AlertTriangle size={11} /> What actually goes wrong
                </h4>
                <ul className="space-y-1">
                  {guide.pitfalls.map((m) => (
                    <li key={m} className="text-[11px] text-text-muted leading-relaxed flex gap-1.5">
                      <span className="text-status-partial shrink-0" aria-hidden>
                        ·
                      </span>
                      {m}
                    </li>
                  ))}
                </ul>
              </section>
            )}
          </div>
        </div>
      )}
    </Card>
  );
}
