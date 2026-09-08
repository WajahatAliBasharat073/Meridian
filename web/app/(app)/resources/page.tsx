"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { ArrowRight, Search } from "lucide-react";
import { PageContainer } from "@/components/layout/PageContainer";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card } from "@/components/ui/card";
import { ResourceRow } from "@/components/concepts/ResourceList";
import { CATEGORY_GROUPS, categoriesInGroup } from "@/lib/conceptCategories";
import { RESOURCES } from "@/lib/resources";
import { cn } from "@/lib/cn";

/** Repositories these links were extracted from, with their licence. The
 * licence column matters: three of them grant no redistribution rights,
 * which is why the clones stay local and gitignored. */
const SOURCE_REPOS: { name: string; url: string; licence: string }[] = [
  { name: "alirezadir/AIMLInterviews", url: "https://github.com/alirezadir/AIMLInterviews", licence: "MIT" },
  { name: "alirezadir/Agentic-AI-Systems", url: "https://github.com/alirezadir/Agentic-AI-Systems", licence: "MIT" },
  { name: "alirezadir/Production-Level-Deep-Learning", url: "https://github.com/alirezadir/Production-Level-Deep-Learning", licence: "no licence" },
  { name: "alexeygrigorev/ai-engineering-field-guide", url: "https://github.com/alexeygrigorev/ai-engineering-field-guide", licence: "no licence" },
  { name: "khangich/machine-learning-interview", url: "https://github.com/khangich/machine-learning-interview", licence: "no licence" },
  { name: "eugeneyan/applied-ml", url: "https://github.com/eugeneyan/applied-ml", licence: "MIT" },
  { name: "EthicalML/awesome-production-machine-learning", url: "https://github.com/EthicalML/awesome-production-machine-learning", licence: "MIT" },
  { name: "alexeygrigorev/data-science-interviews", url: "https://github.com/alexeygrigorev/data-science-interviews", licence: "CC BY 4.0" },
  { name: "rbhatia46/Data-Science-Interview-Resources", url: "https://github.com/rbhatia46/Data-Science-Interview-Resources", licence: "MIT" },
];

export default function ResourcesPage() {
  const [query, setQuery] = useState("");
  const [group, setGroup] = useState<string | null>(null);

  const total = useMemo(
    () => Object.values(RESOURCES).reduce((a, r) => a + r.length, 0),
    []
  );

  const sections = useMemo(() => {
    const q = query.trim().toLowerCase();
    const groups = group ? CATEGORY_GROUPS.filter((g) => g.name === group) : CATEGORY_GROUPS;

    const out = groups.map((g) => ({
      group: g.name,
      cats: categoriesInGroup(g.name)
        .map((meta) => ({
          meta,
          items: (RESOURCES[meta.key] ?? []).filter(
            (r) => !q || r.label.toLowerCase().includes(q) || r.url.toLowerCase().includes(q)
          ),
        }))
        .filter((c) => c.items.length > 0),
    }));

    // "general" holds links the classifier could not confidently place; it
    // belongs to no group, so it is appended rather than silently dropped.
    const general = (RESOURCES["general"] ?? []).filter(
      (r) => !q || r.label.toLowerCase().includes(q) || r.url.toLowerCase().includes(q)
    );
    return { grouped: out.filter((g) => g.cats.length > 0), general: group ? [] : general };
  }, [query, group]);

  const matched =
    sections.grouped.reduce((a, g) => a + g.cats.reduce((b, c) => b + c.items.length, 0), 0) +
    sections.general.length;

  return (
    <PageContainer width="wide">
      <PageHeader
        eyebrow="Career"
        title="Learning Resources"
        description="Courses, papers, engineering blogs and guides, extracted from the nine source repositories and grouped by interview section."
      />

      <Card className="p-4 mb-5">
        <div className="flex flex-col sm:flex-row gap-3 sm:items-center">
          <label className="relative flex-1 min-w-0">
            <Search
              size={15}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-text-faint pointer-events-none"
            />
            <input
              type="search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Filter resources…"
              aria-label="Filter resources"
              className="h-9 w-full rounded-lg border border-border bg-surface-2 pl-9 pr-3 text-sm text-text"
            />
          </label>
          <span className="text-xs text-text-faint tabular-nums shrink-0">
            {matched} of {total}
          </span>
        </div>

        <div className="flex flex-wrap gap-1.5 mt-3">
          {CATEGORY_GROUPS.map((g) => (
            <button
              key={g.name}
              type="button"
              onClick={() => setGroup((cur) => (cur === g.name ? null : g.name))}
              className={cn(
                "h-7 px-2.5 rounded-md text-[11px] font-medium border transition-colors",
                group === g.name
                  ? "border-accent bg-accent-soft text-accent-strong"
                  : "border-border text-text-muted hover:bg-surface-2"
              )}
            >
              {g.name}
            </button>
          ))}
        </div>
      </Card>

      {matched === 0 && (
        <p className="text-sm text-text-muted text-center py-12">
          No resource matches that filter.
        </p>
      )}

      <div className="space-y-8">
        {sections.grouped.map((g) => (
          <section key={g.group}>
            <h2 className="text-sm font-semibold text-text mb-3">{g.group}</h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {g.cats.map(({ meta, items }) => (
                <Card key={meta.key} className="p-4">
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <Link
                      href={`/concepts/${meta.key}`}
                      className="text-sm font-medium text-text hover:text-accent-strong inline-flex items-center gap-1.5"
                    >
                      {meta.label}
                      <ArrowRight size={13} className="text-text-faint" />
                    </Link>
                    <span className="text-xs text-text-faint tabular-nums">{items.length}</span>
                  </div>
                  <ul className="space-y-1">
                    {items.map((r) => (
                      <ResourceRow key={r.url} resource={r} />
                    ))}
                  </ul>
                </Card>
              ))}
            </div>
          </section>
        ))}

        {sections.general.length > 0 && (
          <section>
            <h2 className="text-sm font-semibold text-text mb-1">Unsorted</h2>
            <p className="text-xs text-text-muted mb-3">
              Links the keyword classifier could not confidently place into a section. Kept rather
              than dropped — a mis-filed link is recoverable, a deleted one is not.
            </p>
            <Card className="p-4">
              <ul className="space-y-1">
                {sections.general.map((r) => (
                  <ResourceRow key={r.url} resource={r} />
                ))}
              </ul>
            </Card>
          </section>
        )}
      </div>

      <section className="mt-10">
        <h2 className="text-sm font-semibold text-text mb-1">Where these came from</h2>
        <p className="text-xs text-text-muted mb-3">
          Three of these repositories carry no licence file, so they grant no redistribution rights.
          Their content was read locally for personal study; the clones are gitignored and never
          leave this machine.
        </p>
        <Card className="p-4">
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead>
                <tr className="border-b border-border text-text-faint uppercase tracking-wider">
                  <th className="py-2 px-2">Repository</th>
                  <th className="py-2 px-2">Licence</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/60">
                {SOURCE_REPOS.map((r) => (
                  <tr key={r.name}>
                    <td className="py-2 px-2">
                      <a
                        href={r.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-text-muted hover:text-text"
                      >
                        {r.name}
                      </a>
                    </td>
                    <td
                      className={cn(
                        "py-2 px-2 font-mono",
                        r.licence === "no licence" ? "text-status-partial" : "text-text-faint"
                      )}
                    >
                      {r.licence}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </section>
    </PageContainer>
  );
}
