"use client";

import { useEffect, useState } from "react";
import { ListChecks, RotateCcw, X } from "lucide-react";
import { cn } from "@/lib/cn";
import {
  DSA_CHECKLIST,
  getCheckedItems,
  getPanelOpen,
  setCheckedItems,
  setPanelOpen,
  totalChecklistItemCount,
} from "@/lib/dsaChecklist";

const TOTAL_ITEMS = totalChecklistItemCount();

/** A non-modal companion panel docked to the right edge of the viewport --
 * deliberately not an overlay (unlike NotificationCenter's tray): the
 * point is to work through it *while* still reading/clicking the problem
 * list or a solution elsewhere, not to interrupt with a backdrop. State
 * (which boxes are ticked, and whether the panel is open) persists in
 * localStorage so it survives reloads; there's no "current problem" to
 * scope it to (problems here are browsed, not opened into a dedicated
 * solve screen), so it's a general companion meant to sit beside
 * wherever the code actually gets written, reset by hand between
 * problems via the button at the top. */
export function DsaChecklistPanel() {
  const [open, setOpen] = useState(false);
  const [checked, setChecked] = useState<Record<string, boolean>>({});

  useEffect(() => {
    // Read after mount, same reasoning as NotificationCenter: localStorage
    // doesn't exist during SSR, so a lazy useState initialiser would
    // disagree with the server's HTML and trigger a hydration mismatch.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setOpen(getPanelOpen(false));
    setChecked(getCheckedItems());
  }, []);

  const toggleOpen = () => {
    const next = !open;
    setOpen(next);
    setPanelOpen(next);
  };

  const toggleItem = (id: string) => {
    const next = { ...checked, [id]: !checked[id] };
    setChecked(next);
    setCheckedItems(next);
  };

  const resetAll = () => {
    setChecked({});
    setCheckedItems({});
  };

  const checkedCount = Object.values(checked).filter(Boolean).length;

  return (
    <div className="hidden lg:block">
      {/* Docked toggle tab -- stays visible whether the panel is open or
          closed, so it always doubles as the close control. */}
      <button
        type="button"
        onClick={toggleOpen}
        aria-expanded={open}
        aria-label={open ? "Close problem-solving checklist" : "Open problem-solving checklist"}
        className={cn(
          "fixed top-24 z-40 flex items-center gap-2 rounded-l-xl border border-r-0 border-border bg-surface px-2.5 py-3 shadow-elevated transition-[right] duration-200",
          open ? "right-[340px]" : "right-0"
        )}
      >
        <ListChecks size={16} className="text-accent-strong" />
        <span
          className="text-[11px] font-semibold tracking-wide text-text-muted"
          style={{ writingMode: "vertical-rl" }}
        >
          Checklist {checkedCount > 0 && `(${checkedCount}/${TOTAL_ITEMS})`}
        </span>
      </button>

      {open && (
        <aside
          aria-label="Problem-solving checklist"
          className="fixed right-0 top-16 z-40 h-[calc(100vh-4rem)] w-[340px] border-l border-border bg-surface shadow-elevated flex flex-col"
        >
          <div className="flex items-center justify-between gap-2 px-4 py-3 border-b border-border shrink-0">
            <div>
              <h2 className="text-sm font-semibold text-text">Problem-Solving Checklist</h2>
              <p className="text-[11px] text-text-faint mt-0.5">
                {checkedCount}/{TOTAL_ITEMS} checked
              </p>
            </div>
            <div className="flex items-center gap-1">
              <button
                type="button"
                onClick={resetAll}
                title="Uncheck everything -- start the next problem fresh"
                className="h-8 w-8 flex items-center justify-center rounded-lg text-text-faint hover:text-text hover:bg-surface-2"
              >
                <RotateCcw size={14} />
              </button>
              <button
                type="button"
                onClick={toggleOpen}
                aria-label="Close checklist"
                className="h-8 w-8 flex items-center justify-center rounded-lg text-text-faint hover:text-text hover:bg-surface-2"
              >
                <X size={15} />
              </button>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto px-4 py-3 space-y-4">
            {DSA_CHECKLIST.map((step, i) => (
              <div key={step.id}>
                <div className="flex items-baseline justify-between gap-2 mb-1.5">
                  <h3 className="text-xs font-semibold text-text">
                    Step {i}: {step.title}
                  </h3>
                  <span className="text-[10px] text-text-faint shrink-0">{step.timeEstimate}</span>
                </div>
                <ul className="space-y-1.5">
                  {step.items.map((item) => (
                    <li key={item.id}>
                      <label className="flex items-start gap-2 cursor-pointer group">
                        <input
                          type="checkbox"
                          checked={!!checked[item.id]}
                          onChange={() => toggleItem(item.id)}
                          className="mt-0.5 h-3.5 w-3.5 rounded border-border shrink-0 accent-accent"
                        />
                        <span
                          className={cn(
                            "text-[12px] leading-relaxed",
                            checked[item.id] ? "text-text-faint line-through" : "text-text-muted group-hover:text-text"
                          )}
                        >
                          {item.text}
                        </span>
                      </label>
                      {item.notes && (
                        <ul className="ml-6 mt-1 space-y-0.5">
                          {item.notes.map((note, ni) => (
                            <li key={ni} className="text-[11px] text-text-faint leading-relaxed">
                              {note}
                            </li>
                          ))}
                        </ul>
                      )}
                    </li>
                  ))}
                </ul>
                {i < DSA_CHECKLIST.length - 1 && <div className="border-b border-border mt-3.5" />}
              </div>
            ))}
          </div>
        </aside>
      )}
    </div>
  );
}
