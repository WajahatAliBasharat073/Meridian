"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Check,
  Clock,
  FastForward,
  Lock,
  MoreHorizontal,
  Pause,
  Play,
  RotateCcw,
  Sparkles,
  Volume2,
  X,
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { EARLY_COMPLETION_MESSAGE, isBlockLocked, isTooEarlyToComplete, LOCK_MESSAGE } from "@/lib/blockLock";
import { categoryMeta } from "@/lib/category";
import { formatCountdown, formatTime12h, minutesUntil, nowMinutesInKarachi, timeStringToMinutes } from "@/lib/time";
import {
  completeActiveSession,
  extendActiveSession,
  getActiveSession,
  pauseActiveSession,
  resumeActiveSession,
  shortenActiveSession,
  skipActiveSession,
  startActivitySession,
  subscribeActiveSession,
  type ActiveSession,
} from "@/lib/activityStore";
import { useMarkBlockStatus } from "@/hooks/useMutations";
import { resolveFocusDestination } from "@/lib/focusRouting";
import { pushNotification } from "@/lib/notifications";
import { isPipSupported, openFocusPipWindow } from "@/lib/pipTimer";
import { playSound } from "@/lib/soundEngine";
import type { TimeBlockOut } from "@/lib/types";

export function ActivityController({
  block,
  upcomingBlock,
}: {
  block: TimeBlockOut | null;
  upcomingBlock?: TimeBlockOut | null;
}) {
  const router = useRouter();
  const [session, setSession] = useState<ActiveSession | null>(getActiveSession());
  const [nowSec, setNowSec] = useState<number>(() => Math.floor(Date.now() / 1000));
  const [showRatingModal, setShowRatingModal] = useState(false);
  const [focusRating, setFocusRating] = useState(5);
  const [sessionNotes, setSessionNotes] = useState("");
  const mark = useMarkBlockStatus();

  // Which block we've already fired the end-of-window alert for. Declared
  // with the other hooks, above the early returns below — hook order has to
  // be identical on every render.
  const endAlertedFor = useRef<number | null>(null);

  // Fires once when a running block reaches its scheduled end. Guarded on
  // `block` inside rather than by placement, so the hook still runs when
  // there's no current block.
  useEffect(() => {
    if (!block) return;
    const active = session && session.blockId === block.id;
    if (!active || session.state !== "in_progress") return;

    const remainingSec = Math.round(minutesUntil(block.end, nowMinutesInKarachi()) * 60);
    if (remainingSec > 0) return;
    if (endAlertedFor.current === block.id) return;
    endAlertedFor.current = block.id;

    let worked = session.totalElapsedSeconds;
    worked += Math.max(0, Math.floor(Date.now() / 1000) - Math.floor(session.startTime / 1000));

    playSound("completion");
    pushNotification({
      kind: "activity_complete",
      title: `${block.activity} — time's up`,
      body: `Scheduled to end at ${formatTime12h(block.end)}. ${Math.floor(
        worked / 60
      )}m logged. Mark it done, or keep going and it counts as overrun.`,
      soundType: "completion",
      activityId: block.id,
      activityTitle: block.activity,
      actions: [
        { label: "Complete", action: "start" },
        { label: "Dismiss", action: "dismiss" },
      ],
    });
  }, [block, session, nowSec]);

  // Tick clock every second for precision MM:SS countdown
  useEffect(() => {
    const unsub = subscribeActiveSession((s) => setSession(s));
    const interval = setInterval(() => {
      setNowSec(Math.floor(Date.now() / 1000));
    }, 1000);
    return () => {
      unsub();
      clearInterval(interval);
    };
  }, []);

  if (!block) {
    if (upcomingBlock) {
      const { icon: UpIcon, colorVar: upColor } = categoryMeta(upcomingBlock.category);
      const upcomingLocked = isBlockLocked(upcomingBlock, nowMinutesInKarachi());
      // Same single-active-session rule as the main card below: a session
      // already running for a different block blocks starting this one
      // too, until it's paused or finished.
      const anotherSessionRunning =
        session !== null && session.state === "in_progress" && session.blockId !== upcomingBlock.id;
      return (
        <Card className="p-5 border border-border bg-surface/70 backdrop-blur-sm shadow-sm">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <span
                className="h-11 w-11 rounded-xl flex items-center justify-center shrink-0"
                style={{
                  backgroundColor: `color-mix(in srgb, ${upColor} 15%, transparent)`,
                  color: upColor,
                }}
              >
                <UpIcon size={20} />
              </span>
              <div>
                <span className="text-[10px] font-semibold tracking-wider uppercase text-text-faint">
                  Next Scheduled Anchor
                </span>
                <h3 className="text-sm font-semibold text-text mt-0.5">
                  {upcomingBlock.activity}
                </h3>
                <p className="text-xs text-text-muted mt-0.5">
                  Scheduled {formatTime12h(upcomingBlock.start)} – {formatTime12h(upcomingBlock.end)} ({upcomingBlock.planned_minutes}m · {upcomingBlock.tier})
                </p>
              </div>
            </div>

            {upcomingLocked ? (
              <span
                className="inline-flex items-center gap-1.5 text-xs text-text-faint shrink-0"
                title={LOCK_MESSAGE}
              >
                <Lock size={13} /> Locked — too late to start
              </span>
            ) : anotherSessionRunning ? (
              <OtherSessionControls
                session={session}
                onPause={() => pauseActiveSession()}
                onDiscard={() => skipActiveSession("Abandoned to start a different session")}
              />
            ) : (
              <Button
                size="sm"
                onClick={() => {
                  startActivitySession(
                    upcomingBlock.id,
                    upcomingBlock.activity,
                    upcomingBlock.category,
                    upcomingBlock.planned_minutes,
                    timeStringToMinutes(upcomingBlock.end)
                  );
                  // Must be called directly from this click handler (no
                  // prior await) -- the Picture-in-Picture API requires
                  // the still-live user gesture.
                  void openFocusPipWindow();
                  // The timer is global (lib/activityStore), so navigating
                  // away doesn't stop or lose it -- coming back to Today
                  // later still shows it running.
                  const destination = resolveFocusDestination(
                    upcomingBlock.category,
                    upcomingBlock.activity
                  );
                  if (destination) router.push(destination);
                }}
                className="gap-1.5 shrink-0 bg-accent text-accent-contrast hover:bg-accent-strong"
              >
                <Play size={13} fill="currentColor" /> Start Focus Session
              </Button>
            )}
          </div>
          {upcomingLocked && (
            <p className="text-[11px] text-text-faint mt-2">{LOCK_MESSAGE}</p>
          )}
        </Card>
      );
    }

    return (
      <Card className="p-6 text-center border-dashed border-border bg-surface/40">
        <div className="h-10 w-10 mx-auto rounded-full bg-surface-2 flex items-center justify-center text-text-faint mb-2">
          <Clock size={20} />
        </div>
        <p className="text-text font-medium text-sm">No activity scheduled right now</p>
        <p className="text-text-faint text-xs mt-1">Review the timeline below to start your next session.</p>
      </Card>
    );
  }

  const { icon: Icon, colorVar } = categoryMeta(block.category);
  const isPrayer = block.category === "Prayer";
  const isBlockActive = session && session.blockId === block.id;
  // Only one live session at a time, app-wide -- a session already
  // running for a different block blocks starting this one too, until
  // it's paused or finished. Paused is deliberately not blocking: that's
  // the explicit "stepping away" signal that should free things back up.
  const anotherSessionRunning =
    session !== null && session.state === "in_progress" && !isBlockActive;

  // The headline countdown is always "how long until this block's
  // scheduled end", never "planned duration from when Focus was pressed".
  // The day is a fixed schedule: the next block starts at its own time
  // whether or not this one began late, so starting 30m late leaves 30m
  // less — it does not slide the window 30m later.
  //
  // nowMinutesInKarachi() returns *fractional* minutes (it adds
  // seconds/60), so this is a float and must be rounded before being
  // formatted — `% 60` on it was rendering as "29.00000000000091".
  const nowMin = nowMinutesInKarachi();
  const locked = !isBlockActive && isBlockLocked(block, nowMin);
  const tooEarlyToComplete = isTooEarlyToComplete(block, nowMin);
  const scheduledRemainingSec = Math.round(minutesUntil(block.end, nowMin) * 60);
  const overranBy = scheduledRemainingSec < 0 ? Math.abs(scheduledRemainingSec) : 0;

  // Work actually logged against this block, tracked separately — it is
  // what gets recorded, and it can legitimately differ from the window.
  let workedSec = 0;
  if (isBlockActive) {
    workedSec = session.totalElapsedSeconds;
    if (session.state === "in_progress") {
      workedSec += Math.max(0, nowSec - Math.floor(session.startTime / 1000));
    }
  }

  // Progress = how far through the scheduled window we are, so the bar
  // agrees with the countdown above it.
  const windowSec = Math.max(1, block.planned_minutes * 60);
  const progressPct = Math.min(
    100,
    Math.max(0, Math.round(((windowSec - Math.max(0, scheduledRemainingSec)) / windowSec) * 100))
  );

  const totalRemSec = Math.max(0, scheduledRemainingSec);

  const remHours = Math.floor(totalRemSec / 3600);
  const remMinutes = Math.floor((totalRemSec % 3600) / 60);
  const remSeconds = totalRemSec % 60;
  const timeFormatted =
    remHours > 0
      ? `${remHours}:${String(remMinutes).padStart(2, "0")}:${String(remSeconds).padStart(2, "0")}`
      : `${String(remMinutes).padStart(2, "0")}:${String(remSeconds).padStart(2, "0")}`;

  const handleStart = () => {
    // Defensive: the button dispatching this is already disabled while
    // locked or while another session is running, but a click that lands
    // right at the boundary (or an untrusted DOM event) shouldn't reach
    // the store at all.
    if (locked || anotherSessionRunning) return;
    const endMinutes = parseInt(block.end.split(":")[0], 10) * 60 + parseInt(block.end.split(":")[1], 10);
    startActivitySession(block.id, block.activity, block.category, block.planned_minutes, endMinutes);
    // Must be called directly from this click handler (no prior await) --
    // the Picture-in-Picture API requires the still-live user gesture.
    void openFocusPipWindow();
    pushNotification({
      kind: "activity_start",
      title: block.activity,
      body: `Session started (${block.planned_minutes} min planned)`,
      soundType: "gentle",
      activityId: block.id,
      activityTitle: block.activity,
    });
    // The timer is global (lib/activityStore), so navigating away doesn't
    // stop or lose it -- coming back to Today later still shows it running.
    const destination = resolveFocusDestination(block.category, block.activity);
    if (destination) router.push(destination);
  };

  const handlePause = () => {
    pauseActiveSession();
  };

  const handleResume = () => {
    resumeActiveSession();
  };

  const handleCompleteClick = () => {
    // Completing without ever starting Focus is exactly what "locked"
    // means here; once a session is active, completing it is always fine
    // regardless of how the window looks now. Separately, regardless of
    // engagement, completing more than 5 minutes before the scheduled end
    // is always blocked — the button dispatching this is already disabled
    // in that state, but a click landing right at the boundary shouldn't
    // reach the modal.
    if (!isBlockActive && locked) return;
    if (tooEarlyToComplete) return;
    setShowRatingModal(true);
  };

  // Completing a session running for a *different* block than the one
  // this card is currently showing (see anotherSessionRunning below) --
  // no lock/too-early guard applies, since those are about this card's
  // own scheduled window, not the other block's.
  const handleCompleteOtherSessionClick = () => setShowRatingModal(true);

  const confirmComplete = () => {
    const result = completeActiveSession(focusRating, sessionNotes);
    // Always the session actually being completed, not necessarily this
    // card's own block -- completeActiveSession returns the exact session
    // it just closed out, which is the reliable source of which block to
    // credit whether this card's Complete button was used or the "other
    // running session" one was.
    const targetBlockId = result?.session.blockId ?? block.id;
    const targetActivity = result?.session.activity ?? block.activity;
    const actual = result ? result.actualMinutes : block.planned_minutes;
    mark.mutate({ blockId: targetBlockId, status: "DONE", actualMinutes: actual });
    pushNotification({
      kind: "activity_complete",
      title: "Activity Complete",
      body: `✓ ${targetActivity} — ${actual} focused minutes logged`,
      soundType: "completion",
      activityId: targetBlockId,
    });
    setShowRatingModal(false);
  };

  const handleSkip = () => {
    skipActiveSession("User skipped");
    mark.mutate({ blockId: block.id, status: "NOT DONE" });
  };

  // Clears a session running for a *different*, already-out-of-view block
  // (its own scheduled window has passed, or it was separately marked
  // DONE/NOT DONE via the Timeline row) -- deliberately does not touch
  // that block's status via `mark`, unlike handleSkip: the block's status
  // is whatever the user already set it to through the Timeline, and
  // "discard this stray timer" shouldn't second-guess that.
  const handleDiscardOtherSession = () => {
    skipActiveSession("Abandoned to start a different session");
  };

  return (
    <Card className="p-6 relative overflow-hidden shadow-elevated border-border-strong bg-gradient-to-b from-surface to-surface-2/70">
      {/* Progress Line */}
      <div className="absolute top-0 inset-x-0 h-1 bg-surface-2">
        <div
          className="h-full transition-all duration-1000 ease-linear"
          style={{ width: `${progressPct}%`, backgroundColor: colorVar }}
        />
      </div>

      <div className="flex items-center justify-between gap-2 mb-3">
        <div className="flex items-center gap-2">
          <Icon size={18} style={{ color: colorVar }} aria-hidden />
          <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: colorVar }}>
            {block.category}
          </span>
          {isPrayer && (
            <span className="text-[10px] uppercase font-bold text-prayer bg-prayer-soft px-2 py-0.5 rounded-full border border-prayer/30">
              Essential
            </span>
          )}
        </div>

        {/* State indicator */}
        <div className="flex items-center gap-1.5">
          {isBlockActive && session.state === "in_progress" && (
            <span className="flex items-center gap-1.5 text-xs text-status-done font-medium">
              <span className="h-2 w-2 rounded-full bg-status-done animate-pulse" />
              Focus Active
            </span>
          )}
          {isBlockActive && session.state === "paused" && (
            <span className="flex items-center gap-1.5 text-xs text-status-partial font-medium">
              <span className="h-2 w-2 rounded-full bg-status-partial" />
              Paused
            </span>
          )}
          {block.status === "DONE" && (
            <span className="text-xs text-status-done font-medium flex items-center gap-1">
              <Check size={13} /> Completed
            </span>
          )}
        </div>
      </div>

      {/* Main Activity Title */}
      <div className="flex flex-col sm:flex-row sm:items-baseline justify-between gap-2">
        <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-text text-balance">
          {block.activity}
        </h2>
        <span className="text-xs sm:text-sm text-text-faint tabular-nums shrink-0">
          {formatTime12h(block.start)} &ndash; {formatTime12h(block.end)} ({block.planned_minutes}m)
        </span>
      </div>

      {block.what_to_do && (
        <p className="mt-2 text-xs sm:text-sm text-text-muted leading-relaxed max-w-2xl">
          {block.what_to_do}
        </p>
      )}

      {/* Timer & Controls Bar */}
      <div className="mt-6 pt-4 border-t border-border flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        {/* Big MM:SS Display */}
        <div className="min-w-0">
          <div className="flex items-baseline gap-3 min-w-0">
            <span
              className="text-3xl sm:text-4xl font-mono font-medium tabular-nums tracking-tight shrink-0"
              style={{ color: colorVar }}
            >
              {timeFormatted}
            </span>
            <span className="text-xs text-text-faint font-medium min-w-0 truncate">
              {overranBy > 0 ? (
                <span className="text-status-partial">
                  over by {Math.round(overranBy / 60)}m
                </span>
              ) : (
                <>left until {formatTime12h(block.end)}</>
              )}{" "}
              · {progressPct}% elapsed
            </span>
          </div>

          {/* When a session is running the countdown is the full planned
              duration measured from when Focus was actually pressed — it
              does not shorten just because the start was late. Show that
              lateness explicitly instead of leaving it implied. */}
          {isBlockActive && (
            <p className="text-[11px] text-text-faint mt-1 truncate">
              Started{" "}
              {new Date(session.startTime).toLocaleTimeString("en-US", {
                hour: "numeric",
                minute: "2-digit",
              })}
              {session.startDelayMinutes != null && session.startDelayMinutes > 0 && (
                <span className="text-status-partial">
                  {" "}
                  · {session.startDelayMinutes}m late
                </span>
              )}
              {session.startDelayMinutes != null && session.startDelayMinutes <= 0 && (
                <span className="text-status-done"> · on time</span>
              )}
              {" · "}
              {Math.floor(workedSec / 60)}m worked
            </p>
          )}
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2 flex-wrap">
          {!isBlockActive ? (
            locked ? (
              <span
                className="inline-flex items-center gap-1.5 text-xs text-text-faint"
                title={LOCK_MESSAGE}
              >
                <Lock size={13} /> Locked — too late to start or complete
              </span>
            ) : (
              <>
                {anotherSessionRunning ? (
                  <OtherSessionControls
                    session={session}
                    onPause={handlePause}
                    onComplete={handleCompleteOtherSessionClick}
                    onDiscard={handleDiscardOtherSession}
                  />
                ) : (
                  <Button
                    variant="primary"
                    size="md"
                    onClick={handleStart}
                    className="gap-2 shadow-sm font-semibold"
                  >
                    <Play size={15} className="fill-current" />
                    Start Activity
                  </Button>
                )}
                <Button
                  variant="secondary"
                  size="md"
                  onClick={handleCompleteClick}
                  disabled={tooEarlyToComplete}
                  title={tooEarlyToComplete ? EARLY_COMPLETION_MESSAGE : undefined}
                  className="gap-1.5"
                >
                  <Check size={14} />
                  Done
                </Button>
              </>
            )
          ) : session.state === "in_progress" ? (
            <>
              <Button
                variant="secondary"
                size="md"
                onClick={handlePause}
                className="gap-1.5 font-medium"
              >
                <Pause size={14} />
                Pause
              </Button>
              <Button
                variant="primary"
                size="md"
                onClick={handleCompleteClick}
                disabled={tooEarlyToComplete}
                title={tooEarlyToComplete ? EARLY_COMPLETION_MESSAGE : undefined}
                className="gap-1.5 font-semibold"
              >
                <Check size={15} />
                Complete
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => extendActiveSession(15)}
                title="Add 15 minutes"
                className="text-xs text-text-faint hover:text-text"
              >
                +15m
              </Button>
              {isPipSupported() && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => void openFocusPipWindow()}
                  title="Pop out a floating timer that stays on top of other windows"
                  className="text-xs text-text-faint hover:text-text"
                >
                  Pop out timer
                </Button>
              )}
            </>
          ) : (
            <>
              <Button
                variant="primary"
                size="md"
                onClick={handleResume}
                className="gap-1.5 font-semibold"
              >
                <Play size={14} className="fill-current" />
                Resume
              </Button>
              <Button
                variant="secondary"
                size="md"
                onClick={handleCompleteClick}
                disabled={tooEarlyToComplete}
                title={tooEarlyToComplete ? EARLY_COMPLETION_MESSAGE : undefined}
                className="gap-1.5"
              >
                <Check size={14} />
                Complete
              </Button>
            </>
          )}

          {!isPrayer && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleSkip}
              className="text-xs text-text-faint hover:text-text"
            >
              Skip
            </Button>
          )}
        </div>
      </div>

      {/* Focus Session Rating Modal */}
      {showRatingModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-xs">
          <div className="bg-surface border border-border-strong rounded-2xl p-6 max-w-md w-full shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-semibold text-text">Log Completed Session</h3>
              <button
                onClick={() => setShowRatingModal(false)}
                className="text-text-faint hover:text-text"
              >
                <X size={18} />
              </button>
            </div>

            <div>
              <p className="text-xs text-text-muted mb-2">How was your focus during this session?</p>
              <div className="flex items-center gap-2">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    onClick={() => setFocusRating(star)}
                    className={`flex-1 py-2 rounded-lg border text-sm font-semibold transition-colors ${
                      focusRating === star
                        ? "border-accent bg-accent-soft text-accent-strong"
                        : "border-border bg-surface-2 text-text-faint hover:text-text"
                    }`}
                  >
                    {star} ★
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="text-xs text-text-muted block mb-1">Session notes (optional)</label>
              <textarea
                value={sessionNotes}
                onChange={(e) => setSessionNotes(e.target.value)}
                placeholder="Key takeaways, breakthroughs, or blockers..."
                rows={3}
                className="w-full rounded-lg border border-border bg-surface-2 p-2.5 text-xs text-text resize-none"
              />
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <Button variant="ghost" size="sm" onClick={() => setShowRatingModal(false)}>
                Cancel
              </Button>
              <Button variant="primary" size="md" onClick={confirmComplete}>
                Save & Complete
              </Button>
            </div>
          </div>
        </div>
      )}
    </Card>
  );
}

/** Shown in place of a Start/Focus button whenever the block this card is
 * displaying isn't the one actually running -- gives real Pause/Complete/
 * Discard controls for *that* session right here, since its own block may
 * no longer be "current" (its scheduled window passed) or even visible as
 * NOT DONE (Timeline hides Focus controls once a block is marked DONE),
 * leaving no other way to reach it. Without this, a session left running
 * past its window silently blocks starting anything else with no way out. */
function OtherSessionControls({
  session,
  onPause,
  onComplete,
  onDiscard,
}: {
  session: ActiveSession | null;
  onPause: () => void;
  // Omitted where there's no rating modal in scope to open (the
  // "upcoming block" card returns before that modal's JSX would ever
  // render) -- Pause and Discard alone are still a real way out there.
  onComplete?: () => void;
  onDiscard: () => void;
}) {
  if (!session) return null;
  return (
    <div className="flex items-center gap-2 flex-wrap rounded-lg border border-border bg-surface-2/60 px-3 py-2 w-full">
      <span className="text-xs text-text-muted min-w-0 truncate">
        <span className="font-medium text-text">{session.activity}</span> is still running
      </span>
      <div className="flex items-center gap-1.5 ml-auto shrink-0">
        <Button variant="secondary" size="sm" onClick={onPause} className="gap-1.5">
          <Pause size={12} />
          Pause
        </Button>
        {onComplete && (
          <Button variant="secondary" size="sm" onClick={onComplete} className="gap-1.5">
            <Check size={12} />
            Complete
          </Button>
        )}
        <Button
          variant="ghost"
          size="sm"
          onClick={onDiscard}
          title="Clear this session without saving progress or changing the block's status"
          className="text-text-faint hover:text-danger"
        >
          Discard
        </Button>
      </div>
    </div>
  );
}
