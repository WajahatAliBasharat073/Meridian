"use client";

import { useState } from "react";
import type { FormEvent } from "react";
import {
  BookOpen,
  CheckCircle,
  ChevronDown,
  Clock,
  Flame,
  PenLine,
  Plus,
  Quote,
  Star,
  Trash2,
  X,
} from "lucide-react";
import { PageContainer } from "@/components/layout/PageContainer";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { FieldLabel } from "@/components/ui/field-label";
import { Skeleton } from "@/components/ui/skeleton";
import { QueryError } from "@/components/ui/query-state";
import { EmptyState } from "@/components/ui/empty-state";
import { cn } from "@/lib/cn";
import {
  useAddReadingQuote,
  useCreateReadingBook,
  useDeleteReadingBook,
  useDeleteReadingQuote,
  useLogReadingSession,
  useReadingBooks,
  useReadingStats,
  useUpdateReadingBook,
} from "@/hooks/useReading";
import {
  READING_CATEGORY_LABELS,
  READING_FORMAT_LABELS,
  READING_PRIORITY_LABELS,
  READING_STATUS_LABELS,
} from "@/lib/types";
import type {
  ReadingBookOut,
  ReadingCategory,
  ReadingFormat,
  ReadingPriority,
  ReadingStatus,
} from "@/lib/types";

const STATUS_COLOR: Record<ReadingStatus, string> = {
  to_read: "var(--text-faint)",
  reading: "var(--status-partial)",
  completed: "var(--status-done)",
  paused: "var(--accent)",
  dropped: "var(--danger)",
};

const PRIORITY_COLOR: Record<ReadingPriority, string> = {
  high: "var(--danger)",
  medium: "var(--status-partial)",
  low: "var(--text-faint)",
};

const FORMATS = Object.keys(READING_FORMAT_LABELS) as ReadingFormat[];
const CATEGORIES = Object.keys(READING_CATEGORY_LABELS) as ReadingCategory[];
const STATUSES = Object.keys(READING_STATUS_LABELS) as ReadingStatus[];
const PRIORITIES = Object.keys(READING_PRIORITY_LABELS) as ReadingPriority[];

const VIEW_OPTIONS: { value: string; label: string }[] = [
  { value: "", label: "All books" },
  { value: "reading", label: "Currently reading" },
  { value: "to_read", label: "Want to read" },
  { value: "completed", label: "Completed" },
  { value: "paused", label: "Paused" },
  { value: "dropped", label: "Abandoned" },
  { value: "high_priority", label: "High priority" },
  { value: "needs_revisit", label: "Need to revisit" },
];

export default function ReadingPage() {
  const [view, setView] = useState("");
  const [addOpen, setAddOpen] = useState(false);

  const isHighPriorityView = view === "high_priority";
  const isRevisitView = view === "needs_revisit";
  const statusFilter =
    isHighPriorityView || isRevisitView || view === "" ? undefined : (view as ReadingStatus);

  const { data, isLoading, isError, error, refetch } = useReadingBooks({
    statusFilter,
    needsRevisit: isRevisitView,
  });
  const { data: stats } = useReadingStats();

  const books = (data ?? []).filter((b) => !isHighPriorityView || b.priority === "high");

  return (
    <PageContainer width="wide">
      <PageHeader
        eyebrow="Intellectual Intake"
        title="Reading Log"
        description="Track books, papers, and articles by real position — log the page you reached and completion follows automatically."
        action={
          !addOpen && (
            <Button variant="primary" size="md" onClick={() => setAddOpen(true)} className="gap-1.5">
              <Plus size={15} /> Add Book
            </Button>
          )
        }
      />

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
        <Card className="p-4">
          <p className="text-xs text-text-faint">Currently Reading</p>
          <p className="text-2xl font-bold text-status-partial tabular-nums font-mono mt-1">
            {stats?.reading_count ?? "—"}
          </p>
        </Card>
        <Card className="p-4">
          <p className="text-xs text-text-faint">Completed</p>
          <p className="text-2xl font-bold text-status-done tabular-nums font-mono mt-1">
            {stats?.completed_count ?? "—"}
          </p>
          <p className="text-[10px] text-text-faint mt-0.5">
            {stats ? `${stats.completed_this_month} this month` : ""}
          </p>
        </Card>
        <Card className="p-4">
          <p className="text-xs text-text-faint">Pages This Month</p>
          <p className="text-2xl font-bold text-accent-strong tabular-nums font-mono mt-1">
            {stats?.pages_read_this_month ?? "—"}
          </p>
        </Card>
        <Card className="p-4">
          <p className="text-xs text-text-faint flex items-center gap-1">
            <Flame size={12} /> Reading Streak
          </p>
          <p className="text-2xl font-bold text-text tabular-nums font-mono mt-1">
            {stats ? `${stats.streak_days}d` : "—"}
          </p>
        </Card>
      </div>

      <div className="flex items-center gap-2 mb-4 overflow-x-auto pb-1">
        {VIEW_OPTIONS.map((o) => (
          <button
            key={o.value}
            onClick={() => setView(o.value)}
            className={cn(
              "px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-colors border",
              view === o.value
                ? "bg-surface text-text border-border shadow-xs"
                : "text-text-muted border-transparent hover:bg-surface-2"
            )}
          >
            {o.label}
          </button>
        ))}
      </div>

      {addOpen && <AddBookForm onClose={() => setAddOpen(false)} />}

      {isLoading && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-80" />
          ))}
        </div>
      )}

      {isError && (
        <QueryError error={error} onRetry={() => refetch()} fallback="Couldn't load your reading log." />
      )}

      {data && books.length === 0 && !addOpen && (
        <EmptyState
          icon={BookOpen}
          title={view ? "No books match this view" : "Nothing on your shelf yet"}
          description="Add a book, paper, or article to start tracking real progress — the page you reach, not a guess."
          action={
            <Button variant="primary" size="sm" onClick={() => setAddOpen(true)} className="gap-1.5">
              <Plus size={15} /> Add First Book
            </Button>
          }
        />
      )}

      {books.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {books.map((book) => (
            <BookCard key={book.id} book={book} />
          ))}
        </div>
      )}
    </PageContainer>
  );
}

function AddBookForm({ onClose }: { onClose: () => void }) {
  const createBook = useCreateReadingBook();
  const [title, setTitle] = useState("");
  const [author, setAuthor] = useState("");
  const [coverUrl, setCoverUrl] = useState("");
  const [totalPages, setTotalPages] = useState("");
  const [format, setFormat] = useState<ReadingFormat>("book");
  const [category, setCategory] = useState<ReadingCategory | "">("");
  const [status, setStatus] = useState<ReadingStatus>("reading");
  const [priority, setPriority] = useState<ReadingPriority | "">("");
  const [tagsInput, setTagsInput] = useState("");
  const [whyReading, setWhyReading] = useState("");

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    try {
      await createBook.mutateAsync({
        title: title.trim(),
        author: author.trim() || undefined,
        cover_url: coverUrl.trim() || undefined,
        total_pages: totalPages ? Number(totalPages) : undefined,
        format,
        category: category || undefined,
        status,
        priority: priority || undefined,
        tags: tagsInput.trim()
          ? tagsInput.split(",").map((t) => t.trim()).filter(Boolean)
          : undefined,
        why_reading: whyReading.trim() || undefined,
      });
      onClose();
    } catch {
      // Surfaced via createBook.isError below.
    }
  };

  return (
    <Card className="p-5 mb-6 border-accent/40 bg-gradient-to-b from-surface to-surface-2">
      <form onSubmit={handleSubmit} className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-text">Add to Reading Log</h3>
          <button
            type="button"
            onClick={onClose}
            className="text-text-faint hover:text-text"
            aria-label="Close"
          >
            <X size={16} />
          </button>
        </div>

        <div className="grid sm:grid-cols-2 gap-3">
          <div>
            <FieldLabel>Title</FieldLabel>
            <Input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Deep Work"
              required
            />
          </div>
          <div>
            <FieldLabel hint="optional">Author</FieldLabel>
            <Input
              value={author}
              onChange={(e) => setAuthor(e.target.value)}
              placeholder="e.g. Cal Newport"
            />
          </div>
        </div>

        <div className="grid sm:grid-cols-2 gap-3">
          <div>
            <FieldLabel hint="optional">Cover image URL</FieldLabel>
            <Input
              value={coverUrl}
              onChange={(e) => setCoverUrl(e.target.value)}
              placeholder="https://…"
            />
          </div>
          <div>
            <FieldLabel hint="optional">Total pages</FieldLabel>
            <Input
              type="number"
              min={1}
              value={totalPages}
              onChange={(e) => setTotalPages(e.target.value)}
              placeholder="e.g. 304"
            />
          </div>
        </div>

        <div className="grid sm:grid-cols-3 gap-3">
          <div>
            <FieldLabel>Format</FieldLabel>
            <Select value={format} onChange={(e) => setFormat(e.target.value as ReadingFormat)}>
              {FORMATS.map((f) => (
                <option key={f} value={f}>
                  {READING_FORMAT_LABELS[f]}
                </option>
              ))}
            </Select>
          </div>
          <div>
            <FieldLabel hint="optional">Category</FieldLabel>
            <Select
              value={category}
              onChange={(e) => setCategory(e.target.value as ReadingCategory | "")}
            >
              <option value="">No category</option>
              {CATEGORIES.map((c) => (
                <option key={c} value={c}>
                  {READING_CATEGORY_LABELS[c]}
                </option>
              ))}
            </Select>
          </div>
          <div>
            <FieldLabel>Status</FieldLabel>
            <Select value={status} onChange={(e) => setStatus(e.target.value as ReadingStatus)}>
              {STATUSES.map((s) => (
                <option key={s} value={s}>
                  {READING_STATUS_LABELS[s]}
                </option>
              ))}
            </Select>
          </div>
        </div>

        <div className="grid sm:grid-cols-2 gap-3">
          <div>
            <FieldLabel hint="optional">Priority</FieldLabel>
            <Select
              value={priority}
              onChange={(e) => setPriority(e.target.value as ReadingPriority | "")}
            >
              <option value="">No priority</option>
              {PRIORITIES.map((p) => (
                <option key={p} value={p}>
                  {READING_PRIORITY_LABELS[p]}
                </option>
              ))}
            </Select>
          </div>
          <div>
            <FieldLabel hint="optional, comma-separated">Tags</FieldLabel>
            <Input
              value={tagsInput}
              onChange={(e) => setTagsInput(e.target.value)}
              placeholder="e.g. ml, career"
            />
          </div>
        </div>

        <div>
          <FieldLabel hint="optional">Why you&apos;re reading this</FieldLabel>
          <Input
            value={whyReading}
            onChange={(e) => setWhyReading(e.target.value)}
            placeholder="e.g. Recommended for thesis literature review"
          />
        </div>

        {createBook.isError && (
          <p className="text-xs text-danger">Couldn&apos;t save this book — try again.</p>
        )}

        <div className="flex justify-end gap-2 pt-1">
          <Button type="button" variant="ghost" size="sm" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" variant="primary" size="sm" disabled={createBook.isPending || !title.trim()}>
            {createBook.isPending ? "Saving…" : "Save Book"}
          </Button>
        </div>
      </form>
    </Card>
  );
}

function BookCard({ book }: { book: ReadingBookOut }) {
  const [loggingOpen, setLoggingOpen] = useState(false);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const updateBook = useUpdateReadingBook();
  const deleteBook = useDeleteReadingBook();

  const hasTarget = book.total_pages != null && book.total_pages > 0;
  const pct = book.progress_pct ?? 0;

  return (
    <Card className="p-0 overflow-hidden flex flex-col">
      <div className="flex gap-3 p-4">
        <Cover book={book} />
        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-2">
            <p className="text-sm font-semibold text-text leading-snug text-balance">{book.title}</p>
            <button
              type="button"
              onClick={() => {
                if (confirm(`Remove "${book.title}" from your reading log?`)) {
                  deleteBook.mutate(book.id);
                }
              }}
              className="text-text-faint hover:text-danger shrink-0"
              aria-label="Delete book"
            >
              <Trash2 size={14} />
            </button>
          </div>
          {book.author && <p className="text-xs text-text-muted mt-0.5">{book.author}</p>}
          <div className="flex flex-wrap gap-1.5 mt-2">
            <Badge color={STATUS_COLOR[book.status]}>{READING_STATUS_LABELS[book.status]}</Badge>
            <Badge color="var(--accent)">{READING_FORMAT_LABELS[book.format]}</Badge>
            {book.category && (
              <Badge color="var(--text-faint)">{READING_CATEGORY_LABELS[book.category]}</Badge>
            )}
            {book.priority && (
              <Badge color={PRIORITY_COLOR[book.priority]}>{READING_PRIORITY_LABELS[book.priority]}</Badge>
            )}
          </div>
          {book.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-1.5">
              {book.tags.map((t) => (
                <span key={t} className="text-[10px] text-text-faint">
                  #{t}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="px-4 pb-3">
        {hasTarget ? (
          <>
            <div className="h-1.5 rounded-full bg-surface-2 overflow-hidden">
              <div
                className="h-full rounded-full bg-accent transition-[width]"
                style={{ width: `${Math.min(100, pct)}%` }}
              />
            </div>
            <div className="flex items-center justify-between mt-1.5">
              <p className="text-[11px] text-text-faint tabular-nums">
                {book.current_page != null ? `page ${book.current_page}` : "not started"} / {book.total_pages}
              </p>
              <p className="text-[11px] text-text-faint tabular-nums">{pct}%</p>
            </div>
          </>
        ) : (
          <p className="text-[11px] text-text-faint">
            {book.current_page != null ? `Last on page ${book.current_page} — ` : ""}
            No page target set, so completion can&apos;t be computed.
          </p>
        )}
      </div>

      <div className="px-4 pb-3 flex items-center gap-3 text-[11px] text-text-faint">
        <span className="flex items-center gap-1">
          <Clock size={12} /> {book.total_minutes_logged}m logged
        </span>
        <span>
          {book.session_count} session{book.session_count === 1 ? "" : "s"}
        </span>
        {book.last_session_date && <span>last {book.last_session_date}</span>}
      </div>

      <div className="mt-auto border-t border-border">
        {loggingOpen ? (
          <LogSessionForm book={book} onDone={() => setLoggingOpen(false)} />
        ) : (
          <div className="flex">
            <button
              type="button"
              onClick={() => setLoggingOpen(true)}
              className="flex-1 flex items-center justify-center gap-1.5 h-10 text-xs font-medium text-accent-strong hover:bg-surface-2 transition-colors"
            >
              <PenLine size={13} /> Log today&apos;s page
            </button>
            <button
              type="button"
              onClick={() => setDetailsOpen((v) => !v)}
              className="w-10 flex items-center justify-center text-text-faint hover:text-text hover:bg-surface-2 border-l border-border transition-colors"
              aria-label="More"
            >
              <ChevronDown size={14} className={cn("transition-transform", detailsOpen && "rotate-180")} />
            </button>
          </div>
        )}
      </div>

      {detailsOpen && !loggingOpen && (
        <div className="p-4 border-t border-border space-y-3">
          <div>
            <FieldLabel>Status</FieldLabel>
            <Select
              value={book.status}
              onChange={(e) =>
                updateBook.mutate({ bookId: book.id, input: { status: e.target.value as ReadingStatus } })
              }
            >
              {STATUSES.map((s) => (
                <option key={s} value={s}>
                  {READING_STATUS_LABELS[s]}
                </option>
              ))}
            </Select>
          </div>
          <div>
            <FieldLabel hint="optional">Rating</FieldLabel>
            <div className="flex gap-1">
              {[1, 2, 3, 4, 5].map((n) => (
                <button
                  key={n}
                  type="button"
                  onClick={() =>
                    updateBook.mutate({ bookId: book.id, input: { rating: n } })
                  }
                  aria-label={`Rate ${n} star${n === 1 ? "" : "s"}`}
                >
                  <Star
                    size={16}
                    className={
                      book.rating != null && n <= book.rating
                        ? "fill-accent text-accent"
                        : "text-text-faint"
                    }
                  />
                </button>
              ))}
            </div>
          </div>
          <div>
            <FieldLabel hint="optional">Priority</FieldLabel>
            <Select
              value={book.priority ?? ""}
              onChange={(e) =>
                updateBook.mutate({
                  bookId: book.id,
                  input: { priority: (e.target.value || null) as ReadingPriority | null },
                })
              }
            >
              <option value="">No priority</option>
              {PRIORITIES.map((p) => (
                <option key={p} value={p}>
                  {READING_PRIORITY_LABELS[p]}
                </option>
              ))}
            </Select>
          </div>
          {book.why_reading && (
            <div>
              <FieldLabel>Why you&apos;re reading this</FieldLabel>
              <p className="text-xs text-text-muted leading-relaxed">{book.why_reading}</p>
            </div>
          )}
          <div className="flex items-center justify-between">
            <span className="text-xs text-text-muted">
              {book.revisit_date ? `Flagged to revisit ${book.revisit_date}` : "Not flagged to revisit"}
            </span>
            <Button
              variant="ghost"
              size="sm"
              onClick={() =>
                updateBook.mutate({
                  bookId: book.id,
                  input: book.revisit_date
                    ? { revisit_date: null }
                    : { revisit_date: new Date().toISOString().slice(0, 10) },
                })
              }
            >
              {book.revisit_date ? "Clear" : "Flag to revisit"}
            </Button>
          </div>
          {book.last_session_note && (
            <div>
              <FieldLabel>Last note</FieldLabel>
              <p className="text-xs text-text-muted leading-relaxed">{book.last_session_note}</p>
            </div>
          )}
          <QuotesSection book={book} />
        </div>
      )}
    </Card>
  );
}

function QuotesSection({ book }: { book: ReadingBookOut }) {
  const [adding, setAdding] = useState(false);
  const [text, setText] = useState("");
  const [page, setPage] = useState("");
  const addQuote = useAddReadingQuote();
  const deleteQuote = useDeleteReadingQuote();

  return (
    <div>
      <div className="flex items-center justify-between mb-1.5">
        <FieldLabel>Quotes & highlights</FieldLabel>
        <button
          type="button"
          onClick={() => setAdding((v) => !v)}
          className="text-[11px] text-accent-strong hover:underline"
        >
          {adding ? "Cancel" : "+ Add"}
        </button>
      </div>

      {book.quotes.length > 0 && (
        <ul className="space-y-1.5 mb-2">
          {book.quotes.map((q, i) => (
            <li
              key={`${q.text}-${i}`}
              className="flex items-start gap-2 text-xs text-text-muted leading-relaxed rounded-lg bg-surface-2/50 p-2"
            >
              <Quote size={12} className="shrink-0 mt-0.5 text-text-faint" />
              <span className="flex-1">
                &ldquo;{q.text}&rdquo;
                {q.page != null && <span className="text-text-faint"> — p.{q.page}</span>}
              </span>
              <button
                type="button"
                onClick={() => deleteQuote.mutate({ bookId: book.id, quoteIndex: i })}
                className="text-text-faint hover:text-danger shrink-0"
                aria-label="Delete quote"
              >
                <X size={12} />
              </button>
            </li>
          ))}
        </ul>
      )}

      {adding && (
        <div className="space-y-1.5">
          <Input
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Quote text"
            className="h-9 text-xs"
          />
          <div className="flex gap-1.5">
            <Input
              type="number"
              min={0}
              value={page}
              onChange={(e) => setPage(e.target.value)}
              placeholder="Page (optional)"
              className="h-9 text-xs"
            />
            <Button
              variant="primary"
              size="sm"
              disabled={!text.trim() || addQuote.isPending}
              onClick={() => {
                addQuote.mutate(
                  { bookId: book.id, input: { text: text.trim(), page: page ? Number(page) : undefined } },
                  { onSuccess: () => { setText(""); setPage(""); setAdding(false); } }
                );
              }}
            >
              Save
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

function Cover({ book }: { book: ReadingBookOut }) {
  if (book.cover_url) {
    return (
      // eslint-disable-next-line @next/next/no-img-element
      <img
        src={book.cover_url}
        alt={`Cover of ${book.title}`}
        className="h-24 w-16 shrink-0 rounded-md object-cover border border-border bg-surface-2"
      />
    );
  }
  return (
    <div className="h-24 w-16 shrink-0 rounded-md border border-border bg-surface-2 flex items-center justify-center">
      <BookOpen size={20} className="text-text-faint" />
    </div>
  );
}

function LogSessionForm({ book, onDone }: { book: ReadingBookOut; onDone: () => void }) {
  const logSession = useLogReadingSession();
  const [page, setPage] = useState(book.current_page != null ? String(book.current_page) : "");
  const [minutes, setMinutes] = useState("");
  const [note, setNote] = useState("");

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await logSession.mutateAsync({
        bookId: book.id,
        input: {
          date: new Date().toISOString().slice(0, 10),
          page_reached: page ? Number(page) : undefined,
          minutes: minutes ? Number(minutes) : undefined,
          note: note.trim() || undefined,
        },
      });
      onDone();
    } catch {
      // Surfaced via logSession.isError below.
    }
  };

  return (
    <form onSubmit={handleSubmit} className="p-4 space-y-2.5">
      <div className="grid grid-cols-2 gap-2">
        <div>
          <FieldLabel hint={book.total_pages ? `of ${book.total_pages}` : undefined}>
            Page reached
          </FieldLabel>
          <Input
            type="number"
            min={0}
            max={book.total_pages ?? undefined}
            value={page}
            onChange={(e) => setPage(e.target.value)}
            placeholder="e.g. 128"
            className="h-9 text-xs"
          />
        </div>
        <div>
          <FieldLabel hint="optional">Minutes</FieldLabel>
          <Input
            type="number"
            min={1}
            value={minutes}
            onChange={(e) => setMinutes(e.target.value)}
            placeholder="e.g. 30"
            className="h-9 text-xs"
          />
        </div>
      </div>
      <div>
        <FieldLabel hint="optional">Note</FieldLabel>
        <Input
          value={note}
          onChange={(e) => setNote(e.target.value)}
          placeholder="What stood out today"
          className="h-9 text-xs"
        />
      </div>
      {logSession.isError && <p className="text-xs text-danger">Couldn&apos;t log this session.</p>}
      <div className="flex justify-end gap-2 pt-0.5">
        <Button type="button" variant="ghost" size="sm" onClick={onDone}>
          Cancel
        </Button>
        <Button type="submit" variant="primary" size="sm" disabled={logSession.isPending} className="gap-1.5">
          <CheckCircle size={13} /> {logSession.isPending ? "Saving…" : "Save"}
        </Button>
      </div>
    </form>
  );
}
