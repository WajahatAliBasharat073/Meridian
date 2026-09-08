"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Code2, FileText, Link2, ListPlus, Plus, Trash2, X } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { FieldLabel } from "@/components/ui/field-label";
import { addTopicLearning, deleteTopicLearning, getTopicLearning } from "@/lib/api";
import { cn } from "@/lib/cn";
import type { LearningEntryKind, LearningEntryOut } from "@/lib/types";

const KIND_META: Record<
  LearningEntryKind,
  { label: string; icon: typeof Link2; color: string; hint: string }
> = {
  source: {
    label: "Source",
    icon: Link2,
    color: "var(--accent)",
    hint: "A video, article or course — paste its summary or transcript so the questions can use it.",
  },
  note: {
    label: "Note",
    icon: FileText,
    color: "var(--info)",
    hint: "What you learned, in your own words.",
  },
  snippet: {
    label: "Code",
    icon: Code2,
    color: "var(--status-done)",
    hint: "Code worth keeping. Available to paste in when you verify this topic.",
  },
  requirement: {
    label: "Extra requirement",
    icon: ListPlus,
    color: "var(--status-partial)",
    hint: "Something you decide this topic also demands. It joins the gate checklist.",
  },
};

/** Your record of how you actually learned this topic.
 *
 * Two jobs. It is your own reference library, and it is the context the
 * closed-book questions are aimed with — so they probe the model you built
 * instead of asking generically. It never becomes the *limit* of what you
 * get asked: the gate still forces a question onto something your log does
 * not cover, because otherwise you would be choosing your own exam. */
export function TopicLearningLog({ topic }: { topic: string }) {
  const queryClient = useQueryClient();
  const [adding, setAdding] = useState(false);
  const [kind, setKind] = useState<LearningEntryKind>("source");
  const [title, setTitle] = useState("");
  const [url, setUrl] = useState("");
  const [body, setBody] = useState("");

  const entries = useQuery({
    queryKey: ["topic-learning", topic],
    queryFn: () => getTopicLearning(topic),
  });

  const invalidate = () => {
    void queryClient.invalidateQueries({ queryKey: ["topic-learning", topic] });
    // A self-added requirement changes the gate checklist.
    void queryClient.invalidateQueries({ queryKey: ["topic-checklist", topic] });
  };

  const add = useMutation({
    mutationFn: () =>
      addTopicLearning(topic, {
        kind,
        title: title.trim(),
        url: url.trim() || undefined,
        body: body.trim() || undefined,
      }),
    onSuccess: () => {
      setTitle("");
      setUrl("");
      setBody("");
      setAdding(false);
      invalidate();
    },
  });

  const remove = useMutation({
    mutationFn: (id: number) => deleteTopicLearning(topic, id),
    onSuccess: invalidate,
  });

  const list = entries.data ?? [];
  const meta = KIND_META[kind];

  return (
    <div className="rounded-xl border border-border bg-surface-2/30 p-4">
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="min-w-0">
          <h4 className="text-xs font-semibold text-text">How I&apos;m learning this</h4>
          <p className="text-[11px] text-text-faint mt-0.5 leading-relaxed max-w-lg">
            Log what you studied and the code you keep. The closed-book questions read this,
            so they land on your actual material — but they still cover the checklist,
            including the parts you skipped.
          </p>
        </div>
        {!adding && (
          <Button
            variant="secondary"
            size="sm"
            onClick={() => setAdding(true)}
            className="gap-1.5 shrink-0"
          >
            <Plus size={13} /> Add
          </Button>
        )}
      </div>

      {adding && (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (title.trim()) add.mutate();
          }}
          className="space-y-2.5 mb-3 rounded-lg border border-accent/30 bg-surface p-3"
        >
          <div className="flex items-center justify-between gap-2">
            <span className="text-xs font-medium text-text">New entry</span>
            <button
              type="button"
              onClick={() => setAdding(false)}
              className="text-text-faint hover:text-text"
              aria-label="Cancel"
            >
              <X size={14} />
            </button>
          </div>

          <div className="grid sm:grid-cols-[160px_1fr] gap-2">
            <div>
              <FieldLabel>Kind</FieldLabel>
              <Select
                value={kind}
                onChange={(e) => setKind(e.target.value as LearningEntryKind)}
                className="h-9 text-xs w-full"
              >
                {(Object.keys(KIND_META) as LearningEntryKind[]).map((k) => (
                  <option key={k} value={k}>
                    {KIND_META[k].label}
                  </option>
                ))}
              </Select>
            </div>
            <div>
              <FieldLabel>
                {kind === "requirement" ? "What this topic also needs" : "Title"}
              </FieldLabel>
              <Input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="h-9 text-xs"
                placeholder={
                  kind === "source"
                    ? "e.g. Linked lists — full course"
                    : kind === "requirement"
                      ? "e.g. Cyclic sort for 1..n ranges"
                      : kind === "snippet"
                        ? "e.g. Doubly linked delete"
                        : "e.g. Why prev is needed"
                }
                required
              />
            </div>
          </div>

          <p className="text-[11px] text-text-faint">{meta.hint}</p>

          {kind === "source" && (
            <div>
              <FieldLabel hint="optional">Link</FieldLabel>
              <Input
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="h-9 text-xs"
                placeholder="https://…"
              />
            </div>
          )}

          {kind !== "requirement" && (
            <div>
              <FieldLabel
                hint={kind === "source" ? "this is the part that matters" : "optional"}
              >
                {kind === "source"
                  ? "Summary or transcript — paste it here"
                  : kind === "snippet"
                    ? "Code"
                    : "Details"}
              </FieldLabel>
              <textarea
                value={body}
                onChange={(e) => setBody(e.target.value)}
                rows={kind === "source" ? 6 : 4}
                spellCheck={kind !== "snippet"}
                placeholder={
                  kind === "source"
                    ? "Paste the transcript, or write what it actually taught you. A link on its own tells the questions nothing — nothing here fetches the URL."
                    : kind === "snippet"
                      ? "def delete_at(self, pos): ..."
                      : "What clicked, and what still feels shaky."
                }
                className={cn(
                  "w-full rounded-lg border border-border bg-surface-2 p-2.5 text-xs text-text resize-y",
                  kind === "snippet" && "font-mono"
                )}
              />
            </div>
          )}

          {add.isError && (
            <p className="text-[11px] text-danger">Couldn&apos;t save that entry.</p>
          )}

          <div className="flex justify-end gap-2">
            <Button type="button" variant="ghost" size="sm" onClick={() => setAdding(false)}>
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              size="sm"
              disabled={add.isPending || !title.trim()}
            >
              {add.isPending ? "Saving…" : "Save"}
            </Button>
          </div>
        </form>
      )}

      {entries.isLoading && <p className="text-[11px] text-text-faint">Loading…</p>}

      {!entries.isLoading && list.length === 0 && !adding && (
        <p className="text-[11px] text-text-faint">
          Nothing logged yet. Without it the questions can only work from the checklist and
          your code.
        </p>
      )}

      {list.length > 0 && (
        <ul className="space-y-1.5">
          {list.map((e) => (
            <LearningRow
              key={e.id}
              entry={e}
              onDelete={() => remove.mutate(e.id)}
              deleting={remove.isPending}
            />
          ))}
        </ul>
      )}
    </div>
  );
}

function LearningRow({
  entry,
  onDelete,
  deleting,
}: {
  entry: LearningEntryOut;
  onDelete: () => void;
  deleting: boolean;
}) {
  const [open, setOpen] = useState(false);
  const meta = KIND_META[entry.kind];
  const Icon = meta.icon;
  // A source with no pasted text is the one case worth flagging: it reads as
  // logged work but gives the questions nothing to go on.
  const emptySource = entry.kind === "source" && !entry.body;

  return (
    <li className="rounded-lg border border-border bg-surface px-2.5 py-2">
      <div className="flex items-start gap-2">
        <Icon size={13} className="shrink-0 mt-0.5" style={{ color: meta.color }} aria-hidden />
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs text-text">{entry.title}</span>
            <Badge color={meta.color}>{meta.label}</Badge>
            {entry.url && (
              <a
                href={entry.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-[11px] text-accent-strong hover:underline truncate max-w-[16rem]"
              >
                link
              </a>
            )}
            {emptySource && (
              <span
                className="text-[11px] text-status-partial"
                title="Nothing fetches the link, so this contributes nothing to the questions"
              >
                no summary pasted
              </span>
            )}
          </div>
          {entry.body && (
            <button
              type="button"
              onClick={() => setOpen((v) => !v)}
              className="text-[11px] text-text-faint hover:text-text mt-0.5"
            >
              {open ? "Hide" : `Show ${entry.kind === "snippet" ? "code" : "text"}`}
            </button>
          )}
          {open && entry.body && (
            <pre
              className={cn(
                "mt-1.5 max-h-64 overflow-auto rounded-md border border-border bg-surface-2 p-2 text-[11px] text-text-muted",
                entry.kind === "snippet" ? "font-mono" : "whitespace-pre-wrap font-sans"
              )}
            >
              {entry.body}
            </pre>
          )}
        </div>
        <button
          type="button"
          onClick={onDelete}
          disabled={deleting}
          aria-label={`Delete ${entry.title}`}
          className="shrink-0 text-text-faint hover:text-danger disabled:opacity-40"
        >
          <Trash2 size={13} />
        </button>
      </div>
    </li>
  );
}
