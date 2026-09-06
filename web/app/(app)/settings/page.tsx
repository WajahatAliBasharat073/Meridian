"use client";

import { PageContainer } from "@/components/layout/PageContainer";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card } from "@/components/ui/card";
import { SignOutButton } from "@/components/SignOutButton";
import { AISettingsSection } from "@/components/settings/AISettingsSection";
import { useCurrentUser } from "@/hooks/useCurrentUser";

export default function SettingsPage() {
  const { email } = useCurrentUser();
  const initial = email ? email[0].toUpperCase() : "?";

  return (
    <PageContainer>
      <PageHeader
        eyebrow="Account"
        title="Settings"
        description="Profile and session. Operating parameters (review cap, prayer convention, timezone) live in the database but have no API yet."
      />

      <Card className="p-5">
        <div className="flex items-center gap-4">
          <div
            className="h-12 w-12 rounded-full bg-accent-soft text-accent-strong flex items-center justify-center text-lg font-semibold shrink-0"
            aria-hidden
          >
            {initial}
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-xs font-medium uppercase tracking-wide text-text-faint">Signed in as</p>
            <p className="text-sm text-text mt-0.5 truncate">{email ?? "Loading…"}</p>
          </div>
          <SignOutButton labeled className="w-auto" />
        </div>
      </Card>

      <div className="mt-4">
        <AISettingsSection />
      </div>
    </PageContainer>
  );
}
