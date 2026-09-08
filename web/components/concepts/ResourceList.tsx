"use client";

import { useState } from "react";
import { BookOpen, ExternalLink } from "lucide-react";
import { Card } from "@/components/ui/card";
import { resourcesFor, type Resource } from "@/lib/resources";

const INITIAL = 6;

/** Learning resources for one section.
 *
 * Every link carries the repository it was found in. That is not a
 * courtesy: these were classified by keyword matching on their own titles,
 * which is imperfect, and knowing where a link came from is what lets you
 * judge a mis-filed one instead of trusting it blindly.
 */
export function ResourceList({ category, title = "Resources" }: { category: string; title?: string }) {
  const resources = resourcesFor(category);
  const [expanded, setExpanded] = useState(false);

  if (resources.length === 0) return null;

  const shown = expanded ? resources : resources.slice(0, INITIAL);

  return (
    <Card className="p-5">
      <div className="flex items-center justify-between gap-2 mb-3">
        <h3 className="text-sm font-semibold text-text inline-flex items-center gap-2">
          <BookOpen size={15} className="text-accent-strong" />
          {title}
        </h3>
        <span className="text-xs text-text-faint tabular-nums">{resources.length}</span>
      </div>

      <ul className="space-y-1.5">
        {shown.map((r) => (
          <ResourceRow key={r.url} resource={r} />
        ))}
      </ul>

      {resources.length > INITIAL && (
        <button
          type="button"
          onClick={() => setExpanded((v) => !v)}
          className="mt-3 text-xs text-accent-strong hover:underline"
        >
          {expanded ? "Show fewer" : `Show all ${resources.length}`}
        </button>
      )}
    </Card>
  );
}

export function ResourceRow({ resource }: { resource: Resource }) {
  return (
    <li>
      <a
        href={resource.url}
        target="_blank"
        rel="noopener noreferrer"
        className="group flex items-start gap-2 rounded-lg px-2 py-1.5 -mx-2 hover:bg-surface-2 transition-colors"
      >
        <ExternalLink
          size={12}
          className="mt-1 shrink-0 text-text-faint group-hover:text-accent-strong"
        />
        <span className="min-w-0 flex-1">
          <span className="block text-xs text-text-muted group-hover:text-text leading-relaxed">
            {resource.label}
          </span>
          <span className="block text-[10px] text-text-faint mt-0.5">via {resource.via}</span>
        </span>
      </a>
    </li>
  );
}
