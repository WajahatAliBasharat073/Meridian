import { Check, Lock } from "lucide-react";
import { Badge } from "@/components/ui/badge";

/** A topic's gate state at a glance. Lives here rather than beside the
 * old build/defend dialog it used to ship with, because that flow is
 * gone -- the concept drill is the gate now -- but the badge is still
 * what the topic header renders. */
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
