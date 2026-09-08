"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertTriangle, Check, Eye, Loader2, Lock, ShieldCheck, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { FieldLabel } from "@/components/ui/field-label";
import { Alert } from "@/components/ui/alert";
import { ApiError, getTopicChecklist, submitTopicBuild, submitTopicDefend } from "@/lib/api";
import { cn } from "@/lib/cn";
import type { BuildResultOut, DefendResultOut } from "@/lib/types";

/** Total budget for the closed-book stage. Short on purpose: this is a
 * recall check, and a long timer just invites looking things up. */
const DEFEND_SECONDS = 8 * 60;

type Stage = "build" | "defend" | "result";

/** Records every time the window loses focus during the closed-book stage.
 *
 * This is a flight recorder, not a lock. A browser genuinely cannot prevent
 * tab or window switching — there is no API for it, and a phone defeats any
 * such attempt anyway — so the honest version is to measure it and show it
 * back rather than promise something impossible. */
function useFocusRecorder(active: boolean) {
  const [losses, setLosses] = useState(0);
  const [lostSeconds, setLostSeconds] = useState(0);
  const lostAt = useRef<number | null>(null);

  useEffect(() => {
    if (!active) return;

    const away = () => {
      if (lostAt.current == null) {
        lostAt.current = Date.now();
        setLosses((n) => n + 1);
      }
    };
    const back = () => {
      if (lostAt.current != null) {
        setLostSeconds((s) => s + Math.round((Date.now() - lostAt.current!) / 1000));
        lostAt.current = null;
      }
    };
    const onVisibility = () => (document.hidden ? away() : back());

    window.addEventListener("blur", away);
    window.addEventListener("focus", back);
    document.addEventListener("visibilitychange", onVisibility);
    return () => {
      window.removeEventListener("blur", away);
      window.removeEventListener("focus", back);
      document.removeEventListener("visibilitychange", onVisibility);
    };
  }, [active]);

  return { losses, lostSeconds };
}

export function VerifyTopicDialog({
  topic,
  displayName,
  onClose,
}: {
  topic: string;
  displayName: string;
  onClose: () => void;
}) {
  const queryClient = useQueryClient();
  const [stage, setStage] = useState<Stage>("build");
  const [code, setCode] = useState("");
  const [notes, setNotes] = useState("");
  const [buildResult, setBuildResult] = useState<BuildResultOut | null>(null);
  const [answers, setAnswers] = useState<string[]>([]);
  const [secondsLeft, setSecondsLeft] = useState(DEFEND_SECONDS);
  const [defendResult, setDefendResult] = useState<DefendResultOut | null>(null);
  const startedAt = useRef<number>(0);

  const { losses, lostSeconds } = useFocusRecorder(stage === "defend");

  const checklist = useQuery({
    queryKey: ["topic-checklist", topic],
    queryFn: () => getTopicChecklist(topic),
  });

  const build = useMutation({
    mutationFn: () => submitTopicBuild(topic, { code, notes }),
    onSuccess: (result) => {
      setBuildResult(result);
      if (result.build_passed && result.questions.length > 0) {
        setAnswers(new Array(result.questions.length).fill(""));
        setSecondsLeft(DEFEND_SECONDS);
        startedAt.current = Date.now();
        setStage("defend");
        // Fullscreen makes leaving deliberate rather than accidental. It is
        // not a barrier — Esc exits — and the recorder logs it either way.
        void document.documentElement.requestFullscreen?.().catch(() => {});
      }
    },
  });

  const defend = useMutation({
    mutationFn: () =>
      submitTopicDefend(topic, buildResult!.attempt_id, {
        answers,
        focus_losses: losses,
        focus_lost_seconds: lostSeconds,
        duration_seconds: Math.round((Date.now() - startedAt.current) / 1000),
      }),
    onSuccess: (result) => {
      setDefendResult(result);
      setStage("result");
      if (document.fullscreenElement) void document.exitFullscreen().catch(() => {});
      void queryClient.invalidateQueries({ queryKey: ["problems-by-topic"] });
    },
  });

  const submitDefend = useCallback(() => {
    if (!defend.isPending) defend.mutate();
  }, [defend]);

  // Countdown for the closed-book stage; submits what's there at zero
  // rather than discarding the attempt.
  useEffect(() => {
    if (stage !== "defend") return;
    const id = setInterval(() => {
      setSecondsLeft((s) => {
        if (s <= 1) {
          clearInterval(id);
          submitDefend();
          return 0;
        }
        return s - 1;
      });
    }, 1000);
    return () => clearInterval(id);
  }, [stage, submitDefend]);

  useEffect(() => {
    return () => {
      if (document.fullscreenElement) void document.exitFullscreen().catch(() => {});
    };
  }, []);

  const mm = String(Math.floor(secondsLeft / 60)).padStart(2, "0");
  const ss = String(secondsLeft % 60).padStart(2, "0");
  const unavailable =
    (build.error instanceof ApiError && build.error.status === 503) ||
    (defend.error instanceof ApiError && defend.error.status === 503);

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center p-4 overflow-y-auto bg-black/70 backdrop-blur-xs">
      <div className="bg-surface border border-border-strong rounded-2xl w-full max-w-2xl my-8 shadow-2xl">
        <header className="flex items-start justify-between gap-3 p-5 border-b border-border">
          <div className="min-w-0">
            <p className="text-[10px] uppercase tracking-wide text-text-faint">
              {stage === "build" && "Step 1 of 2 — build"}
              {stage === "defend" && "Step 2 of 2 — closed book"}
              {stage === "result" && "Result"}
            </p>
            <h2 className="text-base font-semibold text-text mt-0.5">
              Prove you understand {displayName}
            </h2>
          </div>
          {stage === "defend" ? (
            <span
              className={cn(
                "shrink-0 font-mono tabular-nums text-sm px-2.5 py-1 rounded-lg border",
                secondsLeft < 60
                  ? "border-danger/40 text-danger"
                  : "border-border text-text-muted"
              )}
            >
              {mm}:{ss}
            </span>
          ) : (
            <button
              onClick={onClose}
              className="text-text-faint hover:text-text shrink-0"
              aria-label="Close"
            >
              <X size={18} />
            </button>
          )}
        </header>

        <div className="p-5 space-y-4">
          {unavailable && (
            <Alert variant="error">
              {build.error instanceof ApiError
                ? build.error.message
                : defend.error instanceof ApiError
                  ? defend.error.message
                  : "Assessment is unavailable."}{" "}
              Nothing was recorded — the gate never passes a topic it could not check.
            </Alert>
          )}

          {/* ---------------- Stage 1: build ---------------- */}
          {stage === "build" && (
            <>
              <p className="text-xs text-text-muted leading-relaxed">
                Implement the items below yourself, then paste the code. It is checked for
                coverage against this list — and immediately afterwards you get a short
                closed-book set of questions, some of them about the code you just pasted.
                That second part is why pasting someone else&apos;s implementation gets you
                nowhere. Anything in this topic&apos;s learning log aims the questions at
                your own material; it never limits them, and one question always targets
                something your log doesn&apos;t cover.
              </p>

              {checklist.isLoading && (
                <p className="text-xs text-text-faint">Loading what this topic requires…</p>
              )}
              {checklist.data && (
                <div>
                  <FieldLabel hint={`${checklist.data.items.length} items`}>
                    Required for {checklist.data.display_name}
                  </FieldLabel>
                  <ul className="grid sm:grid-cols-2 gap-1">
                    {checklist.data.items.map((item) => (
                      <li
                        key={item.text}
                        className={cn(
                          "text-[11px] rounded-md border px-2 py-1",
                          item.self_added
                            ? "border-status-partial/40 bg-status-partial/5 text-text-muted"
                            : "border-border bg-surface-2/40 text-text-muted"
                        )}
                      >
                        {item.text}
                        {item.self_added && (
                          <span className="text-status-partial"> · you added this</span>
                        )}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div>
                <FieldLabel hint="required">Your implementation</FieldLabel>
                <textarea
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  rows={12}
                  spellCheck={false}
                  placeholder={"class Node:\n    def __init__(self, val):\n        ..."}
                  className="w-full rounded-lg border border-border bg-surface-2 p-2.5 text-xs font-mono text-text resize-y"
                />
              </div>

              <div>
                <FieldLabel hint="optional">Your notes</FieldLabel>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  rows={3}
                  placeholder="What clicked, what you had to look up, what still feels shaky."
                  className="w-full rounded-lg border border-border bg-surface-2 p-2.5 text-xs text-text resize-y"
                />
              </div>

              {buildResult && !buildResult.build_passed && (
                <div className="space-y-2">
                  <Alert variant="error">
                    Coverage {Math.round(buildResult.build_score * 100)}% — not enough to move on.
                    Fill the gaps below and submit again.
                  </Alert>
                  {buildResult.missing.length > 0 && (
                    <div>
                      <FieldLabel>Missing</FieldLabel>
                      <div className="flex flex-wrap gap-1.5">
                        {buildResult.missing.map((m) => (
                          <Badge key={m} color="var(--danger)">
                            {m}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                  {buildResult.concerns.length > 0 && (
                    <div>
                      <FieldLabel>Correctness concerns</FieldLabel>
                      <ul className="space-y-1">
                        {buildResult.concerns.map((c) => (
                          <li key={c} className="text-[11px] text-status-partial leading-relaxed">
                            · {c}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              <div className="flex justify-end gap-2 pt-1">
                <Button variant="ghost" size="sm" onClick={onClose}>
                  Cancel
                </Button>
                <Button
                  variant="primary"
                  size="md"
                  disabled={build.isPending || code.trim().length === 0}
                  onClick={() => build.mutate()}
                  className="gap-1.5"
                >
                  {build.isPending ? (
                    <>
                      <Loader2 size={14} className="animate-spin" /> Checking coverage…
                    </>
                  ) : (
                    <>Check and continue</>
                  )}
                </Button>
              </div>
            </>
          )}

          {/* ---------------- Stage 2: defend ---------------- */}
          {stage === "defend" && buildResult && (
            <>
              <div className="rounded-lg border border-border bg-surface-2/40 p-3 space-y-1.5">
                <p className="text-xs text-text flex items-center gap-1.5">
                  <Eye size={13} className="text-text-faint shrink-0" />
                  Closed book. Answer from memory, in your own words.
                </p>
                <p className="text-[11px] text-text-faint leading-relaxed">
                  This cannot actually stop you switching tabs — no web page can. What it does
                  is record it: leaving this window is timestamped and shown on the result.
                  {losses > 0 && (
                    <span className="text-status-partial">
                      {" "}
                      Left {losses} time{losses === 1 ? "" : "s"} so far, {lostSeconds}s away.
                    </span>
                  )}
                </p>
              </div>

              <ol className="space-y-4">
                {buildResult.questions.map((q, i) => (
                  <li key={i}>
                    <p className="text-xs font-medium text-text mb-1.5">
                      {i + 1}. {q}
                    </p>
                    <textarea
                      value={answers[i] ?? ""}
                      onChange={(e) =>
                        setAnswers((prev) => {
                          const next = [...prev];
                          next[i] = e.target.value;
                          return next;
                        })
                      }
                      rows={3}
                      className="w-full rounded-lg border border-border bg-surface-2 p-2.5 text-xs text-text resize-y"
                      placeholder="Two or three sentences."
                    />
                  </li>
                ))}
              </ol>

              <div className="flex items-center justify-between gap-2 pt-1">
                <p className="text-[11px] text-text-faint">
                  Blank answers grade as wrong — that is the point.
                </p>
                <Button
                  variant="primary"
                  size="md"
                  disabled={defend.isPending}
                  onClick={submitDefend}
                  className="gap-1.5"
                >
                  {defend.isPending ? (
                    <>
                      <Loader2 size={14} className="animate-spin" /> Grading…
                    </>
                  ) : (
                    <>Submit answers</>
                  )}
                </Button>
              </div>
            </>
          )}

          {/* ---------------- Result ---------------- */}
          {stage === "result" && defendResult && (
            <>
              <Alert variant={defendResult.passed ? "success" : "error"}>
                {defendResult.passed ? (
                  <>
                    Passed — {displayName} is unlocked for 30 days.{" "}
                    {Math.round(defendResult.defend_score * 100)}% on the closed-book stage.
                  </>
                ) : (
                  <>
                    Not passed — {Math.round(defendResult.defend_score * 100)}% on the
                    closed-book stage. The problems stay locked; the feedback below is what to
                    go back over.
                  </>
                )}
              </Alert>

              {(defendResult.focus_losses > 0 || defendResult.focus_lost_seconds > 0) && (
                <p className="text-[11px] text-status-partial flex items-start gap-1.5">
                  <AlertTriangle size={12} className="shrink-0 mt-0.5" />
                  Recorded: you left the window {defendResult.focus_losses} time
                  {defendResult.focus_losses === 1 ? "" : "s"} for{" "}
                  {defendResult.focus_lost_seconds}s during the closed-book stage. Only you
                  know whether that mattered.
                </p>
              )}

              <ul className="space-y-2.5">
                {defendResult.grades.map((g, i) => (
                  <li key={i} className="rounded-lg border border-border bg-surface-2/40 p-3">
                    <div className="flex items-start justify-between gap-2">
                      <p className="text-xs font-medium text-text">{g.question}</p>
                      <Badge
                        color={
                          g.verdict === "correct"
                            ? "var(--status-done)"
                            : g.verdict === "partial"
                              ? "var(--status-partial)"
                              : "var(--danger)"
                        }
                      >
                        {g.verdict}
                      </Badge>
                    </div>
                    {g.feedback && (
                      <p className="text-[11px] text-text-muted mt-1.5 leading-relaxed">
                        {g.feedback}
                      </p>
                    )}
                  </li>
                ))}
              </ul>

              <div className="flex justify-end pt-1">
                <Button variant="primary" size="md" onClick={onClose} className="gap-1.5">
                  {defendResult.passed ? (
                    <>
                      <ShieldCheck size={15} /> Open the problems
                    </>
                  ) : (
                    <>
                      <Lock size={15} /> Close
                    </>
                  )}
                </Button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export function GateBadge({
  state,
  daysLeft,
  overridden,
}: {
  state: string;
  daysLeft: number | null;
  overridden: boolean;
}) {
  if (state === "unlocked") {
    return (
      <Badge color="var(--status-done)">
        <Check size={11} /> Verified{daysLeft != null && ` · ${daysLeft}d left`}
      </Badge>
    );
  }
  if (state === "expired") {
    return <Badge color="var(--status-partial)">Verification expired</Badge>;
  }
  if (state === "unverified_override") {
    return <Badge color="var(--status-partial)">Unlocked, never verified</Badge>;
  }
  return (
    <Badge color="var(--text-faint)">
      <Lock size={11} /> Locked{overridden ? " · previously overridden" : ""}
    </Badge>
  );
}
