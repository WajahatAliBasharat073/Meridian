"use client";

import { PageContainer } from "@/components/layout/PageContainer";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card } from "@/components/ui/card";
import { SignOutButton } from "@/components/SignOutButton";
import { AISettingsSection } from "@/components/settings/AISettingsSection";
import { SoundSettingsSection } from "@/components/settings/SoundSettings";
import { useCurrentUser } from "@/hooks/useCurrentUser";

export default function SettingsPage() {
  const { email } = useCurrentUser();
  const initial = email ? email[0].toUpperCase() : "?";

  return (
    <PageContainer>
      <PageHeader
        eyebrow="Account & Preferences"
        title="Settings"
        description="Profile, session, audio notification chimes, and AI personal coach configuration."
      />

      <Card className="p-5">
        <div className="flex items-center gap-4">
          <div
            className="h-12 w-12 rounded-full bg-accent-soft text-accent-strong flex items-center justify-center text-lg font-semibold shrink-0"
            aria-hidden
          >
            W
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-xs font-medium uppercase tracking-wide text-text-faint">Signed in as</p>
            <p className="text-base font-semibold text-text mt-0.5 truncate">Wajahat Ali Basharat</p>
            <p className="text-xs text-text-muted mt-0.5 truncate">{email ?? "wajahatalibasharat073@gmail.com"}</p>
          </div>
          <SignOutButton labeled className="w-auto" />
        </div>
      </Card>

      <div className="mt-4 space-y-4">
        <SoundSettingsSection />
        <AISettingsSection />
      </div>
    </PageContainer>
  );
}
