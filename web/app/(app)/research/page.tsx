"use client";

import { useState } from "react";
import {
  Beaker,
  Calendar,
  CheckCircle2,
  Compass,
  ExternalLink,
  FlaskConical,
  Lightbulb,
  Plus,
  Target,
  Trash2,
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
import { formatCountdown } from "@/lib/time";
import { useCreateThesisLog, useThesisLogs } from "@/hooks/useThesis";
import {
  useAddResearchOpportunityToGoals,
  useCreateResearchExperiment,
  useCreateResearchMilestone,
  useCreateResearchNote,
  useCreateResearchOpportunity,
  useCreateResearchPaper,
  useCreateResearchTopic,
  useDeleteResearchOpportunity,
  useDeleteResearchTopic,
  useResearchAtAGlance,
  useResearchExperiments,
  useResearchMilestones,
  useResearchNotes,
  useResearchOpportunities,
  useResearchPapers,
  useResearchTopics,
  useUpdateResearchOpportunity,
  useUpdateResearchTopic,
} from "@/hooks/useResearch";
import {
  RESEARCH_NOTE_KIND_LABELS,
  RESEARCH_OPPORTUNITY_STATUS_LABELS,
} from "@/lib/types";
import type {
  ResearchNoteKind,
  ResearchOpportunityOut,
  ResearchOpportunityStatus,
  ResearchTopicOut,
  ResearchVenueType,
} from "@/lib/types";

type Tab = "glance" | "topics" | "opportunities" | "log";

const TABS: { id: Tab; label: string; icon: typeof Compass }[] = [
  { id: "glance", label: "At a Glance", icon: Compass },
  { id: "topics", label: "Topics", icon: FlaskConical },
  { id: "opportunities", label: "Conferences & Journals", icon: Target },
  { id: "log", label: "Activity Log", icon: Calendar },
];

const OPPORTUNITY_STATUS_COLOR: Record<ResearchOpportunityStatus, string> = {
  interested: "var(--text-faint)",
  shortlisted: "var(--accent)",
  preparing: "var(--status-partial)",
  submitted: "var(--accent-strong)",
  accepted: "var(--status-done)",
  rejected: "var(--danger)",
  not_relevant: "var(--text-faint)",
};

export default function ResearchPage() {
  const [tab, setTab] = useState<Tab>("glance");

  return (
    <PageContainer width="wide">
      <PageHeader
        eyebrow="Academic & R&D"
        title="Research & Thesis"
        description="What am I researching, why, what's next, and what's blocking it -- not just a database of everything."
      />

      <div className="flex items-center gap-1.5 p-1 rounded-xl bg-surface-2 border border-border mb-6 overflow-x-auto">
        {TABS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setTab(id)}
            className={cn(
              "flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold whitespace-nowrap transition-colors",
              tab === id
                ? "bg-surface text-text shadow-xs border border-border"
                : "text-text-muted hover:text-text"
            )}
          >
            <Icon size={14} /> {label}
          </button>
        ))}
      </div>

      {tab === "glance" && <AtAGlanceTab />}
      {tab === "topics" && <TopicsTab />}
      {tab === "opportunities" && <OpportunitiesTab />}
      {tab === "log" && <ActivityLogTab />}
    </PageContainer>
  );
}

// --------------------------------------------------------------- At a Glance

function AtAGlanceTab() {
  const { data, isLoading, isError, error, refetch } = useResearchAtAGlance();

  if (isLoading) return <Skeleton className="h-64" />;
  if (isError) {
    return <QueryError error={error} onRetry={() => refetch()} fallback="Couldn't load research summary." />;
  }
  if (!data) return null;

  return (
    <div className="space-y-4">
      {data.highlights.length > 0 && (
        <Card className="p-4">
          <h3 className="text-sm font-semibold text-text mb-3 flex items-center gap-2">
            <Lightbulb size={15} className="text-accent" /> What matters right now
          </h3>
          <ul className="space-y-2">
            {data.highlights.map((line) => (
              <li
                key={line}
                className="text-sm text-text-muted leading-relaxed pl-3 border-l-2 border-accent/40"
              >
                {line}
              </li>
            ))}
          </ul>
        </Card>
      )}

      <div className="grid sm:grid-cols-2 gap-4">
        <Card className="p-4">
          <p className="text-xs text-text-faint mb-1">Active Topic</p>
          {data.active_topic ? (
            <>
              <p className="text-sm font-semibold text-text">{data.active_topic.title}</p>
              {data.active_topic.description && (
                <p className="text-xs text-text-muted mt-1 leading-relaxed">
                  {data.active_topic.description}
                </p>
              )}
            </>
          ) : (
            <p className="text-xs text-text-faint">No active topic -- add one on the Topics tab.</p>
          )}
        </Card>

        <Card className="p-4">
          <p className="text-xs text-text-faint mb-1">Papers Waiting</p>
          <p className="text-2xl font-bold text-accent-strong tabular-nums font-mono">
            {data.papers_to_read_count}
          </p>
        </Card>
      </div>

      <div className="grid sm:grid-cols-2 gap-4">
        <Card className="p-4">
          <p className="text-xs text-text-faint mb-1">Next Milestone</p>
          {data.next_milestone ? (
            <>
              <p className="text-sm font-semibold text-text">{data.next_milestone.title}</p>
              <p className="text-xs text-text-faint mt-1">{data.next_milestone.target_date}</p>
            </>
          ) : (
            <p className="text-xs text-text-faint">Nothing due in the next 30 days.</p>
          )}
        </Card>

        <Card className="p-4">
          <p className="text-xs text-text-faint mb-1">Next Submission Deadline</p>
          {data.next_opportunity ? (
            <>
              <p className="text-sm font-semibold text-text">{data.next_opportunity.venue_name}</p>
              <p className="text-xs text-text-faint mt-1">{data.next_opportunity.submission_deadline}</p>
            </>
          ) : (
            <p className="text-xs text-text-faint">Nothing due in the next 60 days.</p>
          )}
        </Card>
      </div>
    </div>
  );
}

// --------------------------------------------------------------------- Topics

function TopicsTab() {
  const { data, isLoading, isError, error, refetch } = useResearchTopics();
  const [adding, setAdding] = useState(false);
  const [expanded, setExpanded] = useState<number | null>(null);
  const createTopic = useCreateResearchTopic();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");

  if (isLoading) return <Skeleton className="h-48" />;
  if (isError) {
    return <QueryError error={error} onRetry={() => refetch()} fallback="Couldn't load research topics." />;
  }

  const topics = data ?? [];

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        {!adding && (
          <Button variant="primary" size="md" onClick={() => setAdding(true)} className="gap-1.5">
            <Plus size={15} /> Add Topic
          </Button>
        )}
      </div>

      {adding && (
        <Card className="p-5 border-accent/40 bg-gradient-to-b from-surface to-surface-2">
          <form
            className="space-y-3"
            onSubmit={(e) => {
              e.preventDefault();
              if (!title.trim()) return;
              createTopic.mutate(
                { title: title.trim(), description: description.trim() || undefined },
                { onSuccess: () => { setTitle(""); setDescription(""); setAdding(false); } }
              );
            }}
          >
            <h3 className="text-sm font-semibold text-text">New Research Topic</h3>
            <Input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Topic title" required />
            <Input
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Description (optional)"
            />
            <div className="flex justify-end gap-2">
              <Button type="button" variant="ghost" size="sm" onClick={() => setAdding(false)}>
                Cancel
              </Button>
              <Button type="submit" variant="primary" size="sm" disabled={!title.trim() || createTopic.isPending}>
                {createTopic.isPending ? "Saving…" : "Add Topic"}
              </Button>
            </div>
          </form>
        </Card>
      )}

      {topics.length === 0 && !adding ? (
        <EmptyState
          icon={FlaskConical}
          title="No research topics yet"
          description="Add the direction you're actually working on -- papers, notes, and experiments all attach to a topic."
          action={
            <Button variant="primary" size="sm" onClick={() => setAdding(true)}>
              Add your first topic
            </Button>
          }
        />
      ) : (
        <div className="space-y-2">
          {topics.map((topic) => (
            <TopicCard
              key={topic.id}
              topic={topic}
              expanded={expanded === topic.id}
              onToggle={() => setExpanded(expanded === topic.id ? null : topic.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function TopicCard({
  topic,
  expanded,
  onToggle,
}: {
  topic: ResearchTopicOut;
  expanded: boolean;
  onToggle: () => void;
}) {
  const updateTopic = useUpdateResearchTopic();
  const deleteTopic = useDeleteResearchTopic();
  const [blockerDraft, setBlockerDraft] = useState(topic.current_blocker ?? "");

  return (
    <Card className="p-0 overflow-hidden">
      <div className="p-4 flex items-start justify-between gap-3 cursor-pointer" onClick={onToggle}>
        <div className="min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <p className="text-sm font-semibold text-text">{topic.title}</p>
            <Badge color={topic.status === "active" ? "var(--status-done)" : "var(--text-faint)"}>
              {topic.status}
            </Badge>
          </div>
          {topic.description && (
            <p className="text-xs text-text-muted mt-1 leading-relaxed">{topic.description}</p>
          )}
          {topic.current_blocker && (
            <p className="text-xs text-danger mt-1.5">Blocked: {topic.current_blocker}</p>
          )}
        </div>
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            if (confirm(`Delete "${topic.title}" and its links to papers/notes/experiments?`)) {
              deleteTopic.mutate(topic.id);
            }
          }}
          className="text-text-faint hover:text-danger shrink-0"
          aria-label="Delete topic"
        >
          <Trash2 size={14} />
        </button>
      </div>

      {expanded && (
        <div className="p-4 border-t border-border space-y-4">
          <div className="grid sm:grid-cols-2 gap-2 items-end">
            <div>
              <FieldLabel hint="optional">Current blocker</FieldLabel>
              <Input
                value={blockerDraft}
                onChange={(e) => setBlockerDraft(e.target.value)}
                placeholder="What's stopping progress right now?"
                className="h-9 text-xs"
              />
            </div>
            <div className="flex gap-2">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => updateTopic.mutate({ topicId: topic.id, input: { current_blocker: blockerDraft || null } })}
                disabled={updateTopic.isPending}
              >
                Save
              </Button>
              <Select
                value={topic.status}
                onChange={(e) =>
                  updateTopic.mutate({ topicId: topic.id, input: { status: e.target.value as ResearchTopicOut["status"] } })
                }
                className="h-9 text-xs"
              >
                <option value="active">Active</option>
                <option value="paused">Paused</option>
                <option value="completed">Completed</option>
                <option value="abandoned">Abandoned</option>
              </Select>
            </div>
          </div>

          <TopicPapers topicId={topic.id} />
          <TopicNotes topicId={topic.id} />
          <TopicExperiments topicId={topic.id} />
          <TopicMilestones topicId={topic.id} />
        </div>
      )}
    </Card>
  );
}

function TopicPapers({ topicId }: { topicId: number }) {
  const { data } = useResearchPapers(topicId);
  const createPaper = useCreateResearchPaper();
  const [adding, setAdding] = useState(false);
  const [title, setTitle] = useState("");

  return (
    <div>
      <div className="flex items-center justify-between mb-1.5">
        <FieldLabel>Papers</FieldLabel>
        <button type="button" onClick={() => setAdding((v) => !v)} className="text-[11px] text-accent-strong hover:underline">
          {adding ? "Cancel" : "+ Add"}
        </button>
      </div>
      {(data ?? []).length > 0 && (
        <ul className="space-y-1 mb-2">
          {(data ?? []).map((p) => (
            <li key={p.id} className="text-xs text-text-muted flex items-center gap-2">
              <Badge color="var(--text-faint)">{p.status}</Badge>
              {p.title}
            </li>
          ))}
        </ul>
      )}
      {adding && (
        <div className="flex gap-1.5">
          <Input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Paper title" className="h-8 text-xs" />
          <Button
            size="sm"
            variant="primary"
            disabled={!title.trim() || createPaper.isPending}
            onClick={() => createPaper.mutate({ topic_id: topicId, title: title.trim() }, { onSuccess: () => setTitle("") })}
          >
            Add
          </Button>
        </div>
      )}
    </div>
  );
}

function TopicNotes({ topicId }: { topicId: number }) {
  const { data } = useResearchNotes(topicId);
  const createNote = useCreateResearchNote();
  const [adding, setAdding] = useState(false);
  const [kind, setKind] = useState<ResearchNoteKind>("idea");
  const [content, setContent] = useState("");

  return (
    <div>
      <div className="flex items-center justify-between mb-1.5">
        <FieldLabel>Ideas, questions & notes</FieldLabel>
        <button type="button" onClick={() => setAdding((v) => !v)} className="text-[11px] text-accent-strong hover:underline">
          {adding ? "Cancel" : "+ Add"}
        </button>
      </div>
      {(data ?? []).length > 0 && (
        <ul className="space-y-1 mb-2">
          {(data ?? []).map((n) => (
            <li key={n.id} className="text-xs text-text-muted flex items-start gap-2">
              <Badge color="var(--accent)">{RESEARCH_NOTE_KIND_LABELS[n.kind]}</Badge>
              <span>{n.content}</span>
            </li>
          ))}
        </ul>
      )}
      {adding && (
        <div className="space-y-1.5">
          <Select value={kind} onChange={(e) => setKind(e.target.value as ResearchNoteKind)} className="h-8 text-xs">
            {(Object.keys(RESEARCH_NOTE_KIND_LABELS) as ResearchNoteKind[]).map((k) => (
              <option key={k} value={k}>{RESEARCH_NOTE_KIND_LABELS[k]}</option>
            ))}
          </Select>
          <div className="flex gap-1.5">
            <Input value={content} onChange={(e) => setContent(e.target.value)} placeholder="Content" className="h-8 text-xs" />
            <Button
              size="sm"
              variant="primary"
              disabled={!content.trim() || createNote.isPending}
              onClick={() => createNote.mutate({ topic_id: topicId, kind, content: content.trim() }, { onSuccess: () => setContent("") })}
            >
              Add
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

function TopicExperiments({ topicId }: { topicId: number }) {
  const { data } = useResearchExperiments(topicId);
  const createExperiment = useCreateResearchExperiment();
  const [adding, setAdding] = useState(false);
  const [title, setTitle] = useState("");

  return (
    <div>
      <div className="flex items-center justify-between mb-1.5">
        <FieldLabel>Experiments</FieldLabel>
        <button type="button" onClick={() => setAdding((v) => !v)} className="text-[11px] text-accent-strong hover:underline">
          {adding ? "Cancel" : "+ Add"}
        </button>
      </div>
      {(data ?? []).length > 0 && (
        <ul className="space-y-1 mb-2">
          {(data ?? []).map((exp) => (
            <li key={exp.id} className="text-xs text-text-muted flex items-center gap-2">
              <Badge color="var(--accent)">{exp.status}</Badge>
              {exp.title}
              {exp.result_summary && <span className="text-text-faint">— {exp.result_summary}</span>}
            </li>
          ))}
        </ul>
      )}
      {adding && (
        <div className="flex gap-1.5">
          <Input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Experiment title" className="h-8 text-xs" />
          <Button
            size="sm"
            variant="primary"
            disabled={!title.trim() || createExperiment.isPending}
            onClick={() => createExperiment.mutate({ topic_id: topicId, title: title.trim() }, { onSuccess: () => setTitle("") })}
          >
            Add
          </Button>
        </div>
      )}
    </div>
  );
}

function TopicMilestones({ topicId }: { topicId: number }) {
  const { data } = useResearchMilestones(topicId);
  const createMilestone = useCreateResearchMilestone();
  const [adding, setAdding] = useState(false);
  const [title, setTitle] = useState("");
  const [targetDate, setTargetDate] = useState("");

  return (
    <div>
      <div className="flex items-center justify-between mb-1.5">
        <FieldLabel>Milestones</FieldLabel>
        <button type="button" onClick={() => setAdding((v) => !v)} className="text-[11px] text-accent-strong hover:underline">
          {adding ? "Cancel" : "+ Add"}
        </button>
      </div>
      {(data ?? []).length > 0 && (
        <ul className="space-y-1 mb-2">
          {(data ?? []).map((m) => (
            <li key={m.id} className="text-xs text-text-muted flex items-center gap-2">
              <Badge color={m.status === "completed" ? "var(--status-done)" : "var(--text-faint)"}>{m.status}</Badge>
              {m.title}
              {m.target_date && <span className="text-text-faint">— due {m.target_date}</span>}
            </li>
          ))}
        </ul>
      )}
      {adding && (
        <div className="flex gap-1.5">
          <Input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Milestone title" className="h-8 text-xs" />
          <Input type="date" value={targetDate} onChange={(e) => setTargetDate(e.target.value)} className="h-8 text-xs" />
          <Button
            size="sm"
            variant="primary"
            disabled={!title.trim() || createMilestone.isPending}
            onClick={() =>
              createMilestone.mutate(
                { topic_id: topicId, title: title.trim(), target_date: targetDate || undefined },
                { onSuccess: () => { setTitle(""); setTargetDate(""); } }
              )
            }
          >
            Add
          </Button>
        </div>
      )}
    </div>
  );
}

// --------------------------------------------------------------- Opportunities

function OpportunitiesTab() {
  const { data, isLoading, isError, error, refetch } = useResearchOpportunities();
  const [adding, setAdding] = useState(false);

  if (isLoading) return <Skeleton className="h-48" />;
  if (isError) {
    return <QueryError error={error} onRetry={() => refetch()} fallback="Couldn't load opportunities." />;
  }

  const opportunities = data ?? [];

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        {!adding && (
          <Button variant="primary" size="md" onClick={() => setAdding(true)} className="gap-1.5">
            <Plus size={15} /> Track a Venue
          </Button>
        )}
      </div>

      {adding && <AddOpportunityForm onDone={() => setAdding(false)} />}

      {opportunities.length === 0 && !adding ? (
        <EmptyState
          icon={Target}
          title="No conferences or journals tracked yet"
          description="Track a submission target -- deadline, relevance, and status all in one place."
          action={
            <Button variant="primary" size="sm" onClick={() => setAdding(true)}>
              Track your first venue
            </Button>
          }
        />
      ) : (
        <div className="space-y-2">
          {opportunities.map((o) => (
            <OpportunityCard key={o.id} opportunity={o} />
          ))}
        </div>
      )}
    </div>
  );
}

function AddOpportunityForm({ onDone }: { onDone: () => void }) {
  const createOpportunity = useCreateResearchOpportunity();
  const [venueName, setVenueName] = useState("");
  const [venueType, setVenueType] = useState<ResearchVenueType>("conference");
  const [deadline, setDeadline] = useState("");
  const [researchArea, setResearchArea] = useState("");

  return (
    <Card className="p-5 border-accent/40 bg-gradient-to-b from-surface to-surface-2">
      <form
        className="space-y-3"
        onSubmit={(e) => {
          e.preventDefault();
          if (!venueName.trim()) return;
          createOpportunity.mutate(
            {
              venue_name: venueName.trim(),
              venue_type: venueType,
              submission_deadline: deadline || undefined,
              research_area: researchArea.trim() || undefined,
            },
            { onSuccess: onDone }
          );
        }}
      >
        <h3 className="text-sm font-semibold text-text">Track a Conference or Journal</h3>
        <div className="grid sm:grid-cols-2 gap-2">
          <Input value={venueName} onChange={(e) => setVenueName(e.target.value)} placeholder="Venue name" required />
          <Select value={venueType} onChange={(e) => setVenueType(e.target.value as ResearchVenueType)}>
            <option value="conference">Conference</option>
            <option value="journal">Journal</option>
            <option value="workshop">Workshop</option>
          </Select>
        </div>
        <div className="grid sm:grid-cols-2 gap-2">
          <Input type="date" value={deadline} onChange={(e) => setDeadline(e.target.value)} placeholder="Submission deadline" />
          <Input value={researchArea} onChange={(e) => setResearchArea(e.target.value)} placeholder="Research area (optional)" />
        </div>
        <div className="flex justify-end gap-2">
          <Button type="button" variant="ghost" size="sm" onClick={onDone}>Cancel</Button>
          <Button type="submit" variant="primary" size="sm" disabled={!venueName.trim() || createOpportunity.isPending}>
            {createOpportunity.isPending ? "Saving…" : "Track Venue"}
          </Button>
        </div>
      </form>
    </Card>
  );
}

function OpportunityCard({ opportunity }: { opportunity: ResearchOpportunityOut }) {
  const updateOpportunity = useUpdateResearchOpportunity();
  const deleteOpportunity = useDeleteResearchOpportunity();
  const addToGoals = useAddResearchOpportunityToGoals();

  return (
    <Card className="p-4">
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <p className="text-sm font-semibold text-text">{opportunity.venue_name}</p>
            <Badge color="var(--text-faint)">{opportunity.venue_type}</Badge>
            {opportunity.relevance && (
              <Badge color={opportunity.relevance === "high" ? "var(--status-done)" : "var(--text-faint)"}>
                {opportunity.relevance} relevance
              </Badge>
            )}
          </div>
          {opportunity.research_area && (
            <p className="text-xs text-text-muted mt-1">{opportunity.research_area}</p>
          )}
        </div>
        <button
          type="button"
          onClick={() => {
            if (confirm(`Stop tracking "${opportunity.venue_name}"?`)) deleteOpportunity.mutate(opportunity.id);
          }}
          className="text-text-faint hover:text-danger shrink-0"
          aria-label="Delete opportunity"
        >
          <Trash2 size={14} />
        </button>
      </div>

      <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-text-faint mb-2">
        {opportunity.submission_deadline && <span>Deadline: {opportunity.submission_deadline}</span>}
        {opportunity.event_date && <span>Event: {opportunity.event_date}</span>}
        {opportunity.location && <span>{opportunity.location}</span>}
      </div>

      {opportunity.notes && (
        <p className="text-xs text-text-muted leading-relaxed mb-2">{opportunity.notes}</p>
      )}

      {opportunity.links.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-2">
          {opportunity.links.map((link) => (
            <a
              key={link}
              href={link}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-[11px] text-accent-strong hover:underline"
            >
              {link} <ExternalLink size={10} />
            </a>
          ))}
        </div>
      )}

      <div className="flex items-center justify-between gap-2 pt-2 border-t border-border">
        <Select
          value={opportunity.status}
          onChange={(e) =>
            updateOpportunity.mutate({
              opportunityId: opportunity.id,
              input: { status: e.target.value as ResearchOpportunityOut["status"] },
            })
          }
          className="h-8 text-xs w-auto"
          style={{ color: OPPORTUNITY_STATUS_COLOR[opportunity.status] }}
        >
          {(Object.keys(RESEARCH_OPPORTUNITY_STATUS_LABELS) as ResearchOpportunityOut["status"][]).map((s) => (
            <option key={s} value={s}>{RESEARCH_OPPORTUNITY_STATUS_LABELS[s]}</option>
          ))}
        </Select>
        <Button
          variant="secondary"
          size="sm"
          onClick={() => addToGoals.mutate(opportunity.id)}
          disabled={addToGoals.isPending}
          className="gap-1.5"
        >
          <CheckCircle2 size={13} /> Add to Goals
        </Button>
      </div>
    </Card>
  );
}

// --------------------------------------------------------------- Activity Log

function ActivityLogTab() {
  const { data, isLoading, isError, error, refetch } = useThesisLogs();
  const createLog = useCreateThesisLog();
  const [adding, setAdding] = useState(false);
  const [workSummary, setWorkSummary] = useState("");
  const [milestone, setMilestone] = useState("");
  const [minutes, setMinutes] = useState(60);
  const [outputType, setOutputType] = useState("experiment");

  const logs = data ?? [];
  const timed = logs.filter((l) => l.minutes != null && l.minutes > 0);
  const totalMinutes = timed.reduce((acc, l) => acc + (l.minutes ?? 0), 0);

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!workSummary.trim()) return;
    createLog.mutate(
      {
        date: new Date().toISOString().slice(0, 10),
        work_summary: workSummary.trim(),
        milestone: milestone.trim() || undefined,
        minutes: Number(minutes) || undefined,
        output_type: outputType,
        status: "completed",
      },
      { onSuccess: () => { setWorkSummary(""); setMilestone(""); setAdding(false); } }
    );
  };

  return (
    <div>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-4">
        <Card className="p-4">
          <p className="text-xs text-text-faint">Time logged</p>
          <p className="text-2xl font-bold text-text tabular-nums font-mono mt-1">
            {totalMinutes > 0 ? formatCountdown(totalMinutes) : "—"}
          </p>
        </Card>
        <Card className="p-4">
          <p className="text-xs text-text-faint">Entries</p>
          <p className="text-2xl font-bold text-text tabular-nums font-mono mt-1">{logs.length}</p>
        </Card>
        <Card className="p-4 flex items-center justify-center">
          {!adding && (
            <Button variant="primary" size="sm" onClick={() => setAdding(true)} className="gap-1.5">
              <Beaker size={14} /> Log Research
            </Button>
          )}
        </Card>
      </div>

      {isError && <QueryError error={error} onRetry={() => refetch()} fallback="Couldn't load your thesis log." />}

      {adding && (
        <Card className="p-5 mb-4 border-accent/40 bg-gradient-to-b from-surface to-surface-2">
          <form onSubmit={handleCreate} className="space-y-3">
            <h3 className="text-sm font-semibold text-text">Log Research Output</h3>
            <textarea
              value={workSummary}
              onChange={(e) => setWorkSummary(e.target.value)}
              placeholder="Key findings, derivations, implementation notes..."
              rows={2}
              className="w-full rounded-lg border border-border bg-surface-2 p-2.5 text-xs text-text resize-none"
              required
            />
            <div className="grid sm:grid-cols-3 gap-2">
              <Input value={milestone} onChange={(e) => setMilestone(e.target.value)} placeholder="Milestone (optional)" />
              <Input type="number" value={minutes} onChange={(e) => setMinutes(Number(e.target.value))} />
              <Select value={outputType} onChange={(e) => setOutputType(e.target.value)}>
                <option value="experiment">Experiment</option>
                <option value="paper_reading">Paper Reading</option>
                <option value="thesis_writing">Thesis Writing</option>
                <option value="code_implementation">Code Implementation</option>
              </Select>
            </div>
            <div className="flex justify-end gap-2">
              <Button type="button" variant="ghost" size="sm" onClick={() => setAdding(false)}>Cancel</Button>
              <Button type="submit" variant="primary" size="sm" disabled={createLog.isPending || !workSummary.trim()}>
                {createLog.isPending ? "Saving…" : "Save Entry"}
              </Button>
            </div>
          </form>
        </Card>
      )}

      {isLoading ? (
        <div className="space-y-2">
          {Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-20" />)}
        </div>
      ) : logs.length === 0 ? (
        <EmptyState
          icon={FlaskConical}
          title="No research logs recorded yet"
          description="Log your paper readings, thesis milestones, and experimental findings."
        />
      ) : (
        <ul className="space-y-2">
          {logs.map((log) => (
            <li key={log.id}>
              <Card className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 flex-wrap mb-1">
                    <Badge color="var(--accent)">{log.output_type || "Research"}</Badge>
                    {log.milestone && <span className="text-xs text-text-faint font-medium">· {log.milestone}</span>}
                    <span className="text-[11px] text-text-faint tabular-nums ml-auto sm:ml-0">{log.date}</span>
                  </div>
                  <p className="text-xs text-text leading-relaxed">{log.work_summary}</p>
                </div>
                {log.minutes && (
                  <span className="text-xs font-mono tabular-nums text-text-muted shrink-0">
                    {formatCountdown(log.minutes)}
                  </span>
                )}
              </Card>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
